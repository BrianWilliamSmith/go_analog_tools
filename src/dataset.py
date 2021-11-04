import streamlit as st

def app():
    st.title('🎲 Dataset 🕹')
    st. markdown('''
### Main dataset

The main dataset consists of four tables. The same (anonymized) users are included in both BGGRatings and SteamPlaytimes

- **BGGRatings** : Board games and ratings. Accessed using BGG API 
- **SteamPlaytimes** : Video games and playtimes. Doesn't include games that players own but have never played. Accessed using Steam API
- **BoardGames** : Board game info from BGG for the board games in BGGRatings. No expansions. Accessed using BGG API
- **VideoGames** : Video game info from Steam for the video games in SteamPlaytimes. Accessed by scraping Steam store pages 

[Go Analog Dataset on Go Analog's GitHub](https://github.com/BrianWilliamSmith/go_analog_tools/tree/main/go_analog_dataset)

#### Things you should know if you want to use the data

- Users in the two datasets are *probably* *mostly* the same people
    - A cross-platform user either has the same username in both datasets or has explicitly included their Steam info on their BGG profile (or vice versa)
    - User sameness was primarily checked using their usernames
    - About 20% of initial users were discarded because they had common usernames
    - A username was considered common if it was:
        - Included in the list of English words from NLTK
        - OR
        - Judged to be common by two out of three raters, each of whom rated their impressions of the commonness of every name in the dataset
- Some games don't have data because they're no longer available on Steam or BGG
    - These games have an ID but empty strings for the other columns
- Game names are not unique!
    - Sometimes the same game has multiple (distinct) IDs
- Game names and tags contain quotes, apostrophes, and other bad stuff
    - Be especially careful if you want to parse them into html (as I did with the web app)
- A BGG user can have multiple reviews for the same game
    - This happens when a user reviews a game twice
    - This doesn't occur in the dataset, because I averaged multiple reviews together
- Playtimes and ratings were last updated in December 2020. Newer games won't be in the dataset
- Boardgame and video game data were last updated in October 2021 — rankings, ratings, and tags may have changed!
- To build the recommender, I processed the data by:
    - log-transforming Steam playtimes to deal with extreme outliers 
    - converting ratings and reviews to z-scores to account for the fact that users have different baseline ratings or playtimes

### Description of tables

#### BoardGames.csv

* **Id** : Unique boardgame ID used by BGG
* **Name**
* **Release** : Date formatted as YYYY
* **Rating** : Average game rating on a scale of 1-10, corresponds to Bayes Average in BGG API 
* **Ranking** : Ranking on BGG
* **Subtype_Ranking** : Ranking on BGG out of games in the same game family
* **Subtype_Name** : Name of subtype family for subtype ranking, as displayed on BGG website
    - Examples: "Party Game Rank", "Strategy Game Rank"
* **Time** : Estimated time to complete a game in minutes
* **Min_Age** : Recommended age
* **Min_Players** : Recommended minimum number of players
* **Max_Players** : Recommended maximum number of players
* **Thumbnail** : URL of box art image
* **URL** : URL of BGG game page
* **Tags** : Includes game type, game category, and game mechanics.
    - Example tags for *Codenames: Duet* : "Card Game, Deduction, Spies/Secret Agents, Word Game"

#### VideoGames.csv

* **Id** : Unique game ID used by Steam
* **Name** 
* **Release** : Date formatted as Mon DD, YYYY
* **Rating** : Text string with number of positive or negative ratings
    - Example : "- 75% of the 28,644 user reviews for this game are positive."
* **Rating_Recent** : Positive or negative ratings for the last 30 days
    - Example : "- 75% of the 798 user reviews in the last 30 days are positive."
* **Thumbnail** : URL of Steam thumbnail
* **URL** : URL of Steam page
* **Tags** : User-submitted tags from the Steam store page, listed in descending order of frequency. The store page only displays the first five tags, but the dataset contains all of them (including possibly unreliable tags near end of the list)
    - Example tags for *Microsoft Flight Simulator* : Simulation, Flight, Open World, Realistic, Multiplayer, Singleplayer, Atmospheric, Real-Time, Physics, Adventure, VR, Colorful, Family Friendly, TrackIR, Logic, Life Sim, Surreal, Beautiful, Short, Boxing

#### SteamPlaytimes.csv

* **User** : Anonymized ID
* **Game** : Steam video game ID, foreign key for VideoGames
* **Playtime** : Game playtime across all platforms in minutes

#### BGGRatings.csv

* **User** : Anonymized ID
* **Game** : BGG board game ID, foreign key for BoardGames
* **Rating** : Raw untrasformed boardgame rating

### Web app data

The web app uses four tables, which were all derived from the main dataset. The directory below has the tables along with a Jupyter notebook showing how they were generated.

[Web App Dataset on Go Analog's GitHub](https://github.com/BrianWilliamSmith/go_analog_tools/tree/main/web_app_dataset)


* **ism_bgg.pkl** : A pickled and compressed dataframe containing an item similarity matrix (ISM)
    * The ISM shows cosine similarity between board games and video games, calculated using z scores
    * The similarity scores are between -1 and +1 (since z-scores can be negative)
    * Due to negative similarity scores, you can't use weighted averages to make predictions
    * load with `pd.read_pickle(filename, compression='bz2')`
* **ism_steam.pkl** : Another pickled and compressed datarame with an ISM containing similarity scores between video games and video games (see **ism_bgg.pkl ** above for more info)
* **bg\_info\_for_app.csv** : Used to add board game information to the output tables in the app. Contains html-safe titles, links, tags, etc.
* **vg\_info\_for\_app.csv** : Used to add video game information to the output tables in the app. Contains html-safe titles, links, tags, etc.
''')
