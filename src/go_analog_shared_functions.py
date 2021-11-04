import streamlit as st
import pandas as pd

# Filepaths for video game and board game info
# Used in web app
bg_app_filepath = 'web_app_dataset/bg_info_for_app.csv'
vg_app_filepath = 'web_app_dataset/vg_info_for_app.csv'
ism_bgg_filepath = 'web_app_dataset/ism_bgg.pkl'
ism_steam_filepath = 'web_app_dataset/ism_steam.pkl'

# Functions for loading data
# Separate functions for different dataests so they can all be cached
@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def load_steam_data():
    df = pd.read_pickle(ism_steam_filepath, compression="bz2")
    return df

@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def load_bgg_data():
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
    return df.to_html(index=False, justify='center', escape=False)

def find_similar(platform='steam', reverse=False):
    if platform == 'steam':
        dataset = load_steam_data()
    if platform == 'bgg':
        dataset = load_bgg_data()
  
    form = st.form(key='my_key')
    game = form.selectbox("Select video game", options=dataset.columns)
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
        st.markdown("### The "+str(n)+" "+type_of_game+" games "+comparative+" similar to "+game)
        st.write('<br><br>', unsafe_allow_html=True)
        st.write(out, unsafe_allow_html=True)
