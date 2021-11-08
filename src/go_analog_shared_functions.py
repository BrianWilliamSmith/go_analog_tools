import streamlit as st
import pandas as pd
import numpy as np
import random as rd
import requests as rq
import json
import os

# Filepaths for video game and board game info
# Used in web app
bg_app_filepath = 'web_app_dataset/bg_info_for_app.csv'
vg_app_filepath = 'web_app_dataset/vg_info_for_app.csv'
ism_bgg_filepath = 'web_app_dataset/ism_bgg.pkl'
ism_steam_filepath = 'web_app_dataset/ism_steam.pkl'

# Functions for loading data
# Separate functions for different dataests so they can all be cached

@st.cache(hash_funcs={pd.DataFrame: lambda _: None}, show_spinner=False)
def load_steam_data():
    with st.spinner("Please wait. Loading video game ⮕ video game item similarity matrix…"):
        df = pd.read_pickle(ism_steam_filepath, compression="bz2")
        return df


@st.cache(hash_funcs={pd.DataFrame: lambda _: None}, show_spinner=False)
def load_bgg_data():
    with st.spinner("Please wait. Loading video game ⮕ board game item similarity matrix…"):
        df = pd.read_pickle(ism_bgg_filepath, compression="bz2")
        return df


@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def load_bg_data_for_web_app():
    return pd.read_csv(bg_app_filepath)


@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def load_vg_data_for_web_app():
    return pd.read_csv(vg_app_filepath)


def find_similar_games(game_name, item_sim_matrix):
    # Returns 2-column data frame
    try:
        out = item_sim_matrix[game_name].sort_values(ascending=False)
        out = out[1:]
        out = pd.DataFrame(zip(out.index,out), columns=['Game','Similarity Score'])
        return out 
    except:
        return 'Game not in database'


def annotate_table(df, left_on='Game', right_on='Name', platform='bgg'):
    if platform == 'bgg':
        dataset = load_bg_data_for_web_app()
    if platform == 'steam':
        dataset = load_vg_data_for_web_app()
    df = df.merge(dataset, left_on=left_on, right_on=right_on)
    return df


def rearrange_table(df, columns_to_show, order_by='Title', how_many_rows=10,
                    desc=False, reverse=False):
    if reverse == False:
        df = df.head(how_many_rows)
    else:
        df = df.tail(how_many_rows)
    df = df.sort_values(by = [order_by], ascending = not desc)
    return df[columns_to_show]


def render_table(df):
    out = df.to_html(index=False, justify='center', escape=False)
    out = out.replace('<td>', '<td align="center" valign="center">')
    return out


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


@st.cache(show_spinner=False, suppress_st_warning=True)
def recommend_games(games,
    platform='bgg', 
    min_neighbors=3, 
    neighbor_cutoff=0.15, 
    based_on_n=3,
    popular_games=True):
    '''
    Takes list of (game, ratings) tuples and returns pandas dataframe
    '''
   
    game_names = [game_name for (game_name, playtime) in games] 
    playtimes = [playtime for (game_name, playtime) in games] 
    
    # Item similarity matrix -- df with video games as columns, board or board games as rows
    # For video games, remove rows corresponding to already owned games
    if platform == 'bgg':
        ism = load_bgg_data()
    else:
        ism = load_steam_data()
        ism = ism.loc[~ism.index.isin(game_names)]
 
    # Only include columns for games that user has played
    ism = ism[game_names]
    
    with st.spinner("Please wait. Finding similar games…"):

        # Find board games with minimum number of neighbors
        neighbor_counts = ism[ism >= neighbor_cutoff].count(axis=1) 
        games_with_neighbors = neighbor_counts[neighbor_counts >= min_neighbors].index.tolist()
        
        # Dictionary containing list of neighbors
        based_on_games_you_play = {}

        if len(games_with_neighbors)>0:
            
            # Dictionary with 3 most similar neighbors for every game with neighbors
            for game in games_with_neighbors:
                sim_games = ism.loc[games_with_neighbors].transpose()[game].nlargest(based_on_n).index.tolist()
                based_on_games_you_play.update({game:'You play…<br>' + '<br>'.join(sim_games)})
            
            # Predict scores for games with neighbors
            user_item_neighbors = ism.loc[games_with_neighbors].to_numpy()
            predictions = user_item_neighbors.dot(playtimes)
        
            # Z transform so predicted scores are comparable to average game ratings
            # Can't use weighted average because some similarity scores are negative
            predictions = (predictions - predictions.mean()) / predictions.std()

            predictions = predictions.round(2)
        
            # Dictionary with name+rating for every game with neighbors
            game_ratings = dict(zip(games_with_neighbors, predictions))
            
        else:
            print('There are no similar board games in the dataset. Try changing advanced settings.')
            game_ratings = {} 

        # Use prediction if there are neighbors, otherwise use average
        # Returns predicted score of -100 if a boardgame isn't in the dataset
        output = []
        
        # Dict with global average for every bg
        if popular_games:
            if platform=='bgg':
                averages = load_bg_data_for_web_app()
            else:
                averages = load_vg_data_for_web_app()
            averages = dict(zip(averages.Name, averages['Average Rating Z'].round(2)))

        # Empty dict of averages if user doesn't want popular games reccommended
        else:
            averages = {}

        for game in ism.index:
            output.append(
                (game, 
                 game_ratings.get(game, averages.get(game, -100)),
                 based_on_games_you_play.get(game, "It's a popular game (rank predicted using dataset average)"))
            )
        
        output_df = pd.DataFrame(output, columns=['Game', 'Score', 'Recommended because…']).sort_values('Score', ascending=False)
        output_df = output_df[output_df.Score>-100]
        output_df['My Ranking'] = ['#' + str(x) for x in(output_df.reset_index().index + 1)]
    
    return output_df


def find_similar(platform='steam', reverse=False):
    if platform == 'steam':
        dataset = load_steam_data()
    if platform == 'bgg':
        dataset = load_bgg_data()
  
    form = st.form(key='my_key')
    game_options = dataset.columns.sort_values()
    game = form.selectbox("Select video game", options=game_options)
    n = form.slider("Number of games", 5, 50, 10)
    reverse = form.checkbox("Show least similar games instead")
    submit = form.form_submit_button("Find similar games")

    if platform == 'steam':
        platform_cols = ['Steam Rating']
        type_of_game = 'video'
    else:
        platform_cols = ['BGG Rating','BGG Ranking']
        type_of_game = 'board'

    columns_to_show = ['Similarity Score','Title','Release'] + \
                        platform_cols + ['Tags']

    if submit:
        out = find_similar_games(game, dataset)
        out = annotate_table(out, platform=platform)
        out = rearrange_table(out, columns_to_show, how_many_rows=n, reverse=reverse,
                              order_by='Similarity Score', desc=not reverse)
        out = render_table(out)
        
        video_games = load_vg_data_for_web_app()
        target_game = video_games[video_games.Name==game]
        columns_to_show = ['Title','Release','Steam Rating','Tags']
        target_game = rearrange_table(target_game, columns_to_show)
        target_game = render_table(target_game)

        if reverse:
            comparative = " least"
        else:
            comparative = " most"
    
        st.write(target_game, unsafe_allow_html=True)
        st.write('<br>', unsafe_allow_html=True)
        st.markdown("### The " + str(n) + " " + type_of_game + " games " + comparative + " similar to " + game)
        st.write(out, unsafe_allow_html=True)


def go_analog_app(platform='bgg'):

    # Input form and interface
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

    if platform == 'bgg':
        
        game_type = 'board'

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
        
        show_columns = ['Title',
                        'My Ranking',
                        'BGG Ranking',
                        'BGG Rating',
                        'Release',
                        'Tags',
                        'Recommended because…']
    else:

        game_type = 'video'

        sort_by_selection = form.selectbox("Sort by column…", ("My Ranking",
                                                        "Title",
                                                        "Steam Rating (desc)",
                                                        "Release (desc)"))

        column_settings = {'My Ranking':('Score', not reverse),
                       'Steam Rating (desc)':('Steam Rating', True),
                       'Title':('Name', False),
                       'Release (desc)':('Release', True)}


        show_columns = ['Title',
                        'My Ranking',
                        'Steam Rating',
                        'Release',
                        'Tags',
                        'Recommended because…']

    sort_by, desc = column_settings.get(sort_by_selection)

    if hidden_scores:
        show_columns += ['Score']

    submit_string = 'Recommend ' + game_type + ' games'
    submit = form.form_submit_button(submit_string)

    # Run when form is submitted
    
    if submit:
        my_steam_key = os.environ.get('API_KEY')

        if my_steam_key == None:
            st.error("Steam API key either isn't available")
            st.stop()

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

        games_out = recommend_games(vgs,
                         platform=platform, 
                         min_neighbors=min_neighbors, 
                         neighbor_cutoff=neighbor_cutoff,
                         popular_games=popular_games,
                         based_on_n=based_on_n)
        
        games_out = annotate_table(games_out, platform=platform)

        if reverse:
            games_out = games_out[games_out.Score < 0]
        else: 
            games_out = games_out[games_out.Score > 0]
        
        if len(games_out) == 0:
            st.error("No games to recommend! Try using the advanced options, or click the checkbox to include popular games in results.")
            st.stop()

        games_out = rearrange_table(games_out, show_columns, sort_by, how_many, desc, reverse)
        
        games_out = render_table(games_out)
        
        st.write(games_out, unsafe_allow_html=True)
