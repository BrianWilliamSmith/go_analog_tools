import streamlit as st
import pandas as pd
import numpy as np
from src.go_analog_shared_functions import *
import requests as rq
import json

def get_games(steam_id, steam_api_key):
    '''
    Returns a list of (game ids, playtime) tuples
    '''
    req = rq.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={id}&include_played_free_games=1&include_appinfo=1'\
                 .format(key=steam_api_key, id=steam_id))

    if req.status_code == 500:
        return("500")

    if json.loads(req.text).get('response').get('games') == None:
        return("No games")

    else:
        games_list = json.loads(req.text).get('response').get('games') # List of dictionaries
        out =[(game.get('appid'), game.get('playtime_forever')) for game in games_list \
              if game.get('playtime_forever') > 0]
         
        # Key to convert between game names and ids
        id_name_key = load_vg_data_for_web_app()[['Id','Name']]
        id_name_key = dict(zip(id_name_key.Id, id_name_key.Name))
        
        out = [(id_name_key.get(game_id), playtime)\
               for (game_id, playtime) in out if game_id in id_name_key.keys()]
    
        return out


def normalize_ratings(game_ratings, cutoff=10, z_scores = True):
    '''
    Takes a list of (game, ratings) tuples, prunes games with playtimes
    less than cutoff, log-transforms, and returns list of (game,Z-scores) tuples
    
    '''    
    # Must play for at least n minutes
    game_ratings = [(id,rating) for (id,rating) in game_ratings if rating >= cutoff]

    # Log transform (playtimes are very left skewed)
    games = [id for (id,rating) in game_ratings]
    ratings = np.log([rating for (id,rating) in game_ratings])

    # Z_score
    if z_scores:
        mean = np.mean(ratings)
        std = np.std(ratings)
        ratings = (ratings-mean)/std

    return(list(zip(games, ratings)))


@st.cache(suppress_st_warning=True)
def recommend_boardgames(vgs, 
                         ism, 
                         min_neighbors=2, 
                         neighbor_cutoff=0.15, 
                         based_on_n=3,
                         popular_games=True):
    '''
    Takes list of (game, ratings) tuples and returns pandas dataframe
    '''
   
    vg_names = [game_name for (game_name, playtime) in vgs] 
    playtimes = [playtime for (game_name, playtime) in vgs] 
    
    # Item similarity matrix -- df with video games as columns, board games as rows
    # Only include video games that user has played
    df = ism[vg_names]
    
    # Find board games with minimum number of neighbors
    bg_neighbor_counts = df[df>=neighbor_cutoff].count(axis=1) 
    bgs_with_neighbors = bg_neighbor_counts[bg_neighbor_counts>=min_neighbors].index.tolist()
    
    # Dictionary containing list of neighbors
    based_on_games_you_play = {}

    if len(bgs_with_neighbors)>0:
        
        # Dictionary with 3 most similar neighbors for every bg with neighbors
        for bg in bgs_with_neighbors:
            sim_games = df.loc[bgs_with_neighbors].transpose()[bg].nlargest(based_on_n).index.tolist()
            based_on_games_you_play.update({bg:'You play…<br>' + '<br>'.join(sim_games)})
        
        # Predict scores for bgs with neighbors
        user_item_neighbors = df.loc[bgs_with_neighbors].to_numpy()
        predictions = user_item_neighbors.dot(playtimes)
    
        # Z transform so predicted scores are comparable to average bg ratings
        # Can't use weighted average because some similarity scores are negative
        predictions = (predictions - predictions.mean()) / predictions.std()
    
        # Dictionary with name+rating for every bg with neighbors
        game_ratings = dict(zip(bgs_with_neighbors, predictions))
        
    else:
        st.error("There aren't enough sufficiently similar boardgames to make personalized recommendations. Try selecting more video games or changing the advanced options. Or, you can use the Convert VG ⮕ BG tool.")
        game_ratings = {} 

    # Use prediction if there are neighbors, otherwise use average
    # Returns predicted score of -100 if a boardgame isn't in the dataset
    output = []
    
    # Dict with global average for every bg
    if popular_games:
        bg_averages = load_bg_data_for_web_app()
        bg_averages = dict(zip(bg_averages.Name, bg_averages['Average Rating Z'].round(2)))

    # Empty dict of averages if user doesn't want popular games reccommended
    else:
        bg_averages = {}

    for bg in df.index:
        output.append(
            (bg, 
             game_ratings.get(bg, bg_averages.get(bg, -100)),
             based_on_games_you_play.get(bg, "It's a popular game (rank predicted using average rating)"))
        )
    
    output_df = pd.DataFrame(output, columns=['Game', 'Score', 'Recommended because…']).sort_values('Score', ascending=False)
    output_df = output_df[output_df.Score>-100]

    output_df['Score'] = output_df.Score.round(3)
    output_df['My Ranking'] = ['#' + str(x) for x in(output_df.reset_index().index + 1)]
    
    return output_df


def app():

    st.title('🎲 Go Analog 🕹')
    st.header('Recommend board games based on your Steam profile')

    # Input forms
    form = st.form(key='my_key')
    
    steam_id = form.text_input("Enter 16-digit Steam ID", '76561198026189780')
    popular_games = not form.checkbox("Only show personalized recommendations (don't recommend a game just because it's popular)")

    min_selected_games = 3

    with form.expander("Manually select video games (overrides Steam ID)"):
        selected_games = st.multiselect("Select at least " + str(min_selected_games) + " video games", 
            options=sorted(load_vg_data_for_web_app().Name.tolist()))

    with form.expander("Advanced options for fiddling and debugging",):
        how_many = st.slider("Number of games to recommend", 1, 20, 10)
        min_neighbors = st.slider("Minimum number of neighbors required to predict a rating", 1, 10, 2)
        neighbor_cutoff = st.slider("Minimum similarity score required for two games to be neighbors", .05, .25, .10)
        based_on_n = st.slider("Number of games to report in 'Recommended because…' column", 1, 5, 3)
        hidden_scores = st.checkbox("Show predicted scores (z-score for predicted games)")
        reverse = st.checkbox("Show games you'd probably hate (why are you doing this!)")

    sort_by_selection = form.selectbox("Sort by column…", ("My Ranking",
                                                            "Title",
                                                           "BGG Ranking",
                                                           "BGG Rating (desc)",
                                                           "Release (desc)"))

    column_settings = {'My Ranking':('Score', not reverse),
                       'BGG Rating (desc)':('BGG Rating', True),
                       'BGG Ranking':('BGG Ranking', False),
                       'Title':('Name', False),
                       'Release (desc)':('Release', True)}
    

    sort_by, desc = column_settings.get(sort_by_selection)

    show_columns = ['Title',
                    'My Ranking',
                    'BGG Ranking',
                    'BGG Rating',
                    'Release',
                    'Tags',
                    'Recommended because…']

    if hidden_scores:
        show_columns += ['Score']

    submit = form.form_submit_button("Recommend board games")

    # Run when form is submitted
    if submit:
        ism = load_bgg_data()
        my_steam_key = open("key.txt").read()

        if len(selected_games) > 0:
            if len(selected_games) < min_selected_games:
                st.error("Pleaes select at least " + str(min_selected_games) + " video games")
                st.stop()

            vgs = [(game, 2) for game in selected_games]

        else:
            vgs = get_games(steam_id, my_steam_key)

            if vgs == '500':
                st.error("No luck finding user! Not a valid Steam ID?")
                st.stop()

            if vgs == 'No games':
                st.error("No luck find games playtimes! Are games set to private?")
                st.stop()

            vgs = normalize_ratings(vgs)

        bgs = recommend_boardgames(vgs,
                         ism, 
                         min_neighbors=min_neighbors, 
                         neighbor_cutoff=neighbor_cutoff,
                         popular_games=popular_games,
                         based_on_n=based_on_n)
        
        bgs = annotate_table(bgs)

        if reverse:
            bgs = bgs[bgs.Score < 0]
        else: 
            bgs = bgs[bgs.Score > 0]
        
        if len(bgs) == 0:
            st.error("No games to recommend! Try using the advanced options or including popular games.")
            st.stop()

        bgs = rearrange_table(bgs, show_columns, sort_by, how_many, desc, reverse)
        
        bgs = render_table(bgs)
        
        st.write(bgs, unsafe_allow_html=True)

