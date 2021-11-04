import streamlit as st

def app():

    st.title('🎲 Home 🕹')
    st.markdown('''

### Welcome!

I'm Brian, and I developed Go Analog as a portfolio project, fueled by a love of all types of gaming. You can find everything [on Github](https://github.com/BrianWilliamSmith/go_analog_tools/).

- **Go Analog** recommends board games that are similar to your favorite video games
   - The recommender requires an account on the videogaming platform Steam
   - Enter your 9-digit Steam ID and make sure your video game playtime isn't set to private
   - Go Analog will access your video game play history and make personalized recommendations for board games
- If you don't have a Steam account, or if you just want to play with the similarity model, you can use the conversion tools to select a video game and explore similar video or board games 
    - You can also use one of these Steam IDs, each of which has publically accessible profiles (at the time of writing):
        - 76561198018010017, 76561198029016376, 76561198012840749, 76561198011832660, 76561198312338396, 76561197969480861
- All of the tools were built using a home-brewed dataset of users' video game playtimes and board game ratings
    - The data was collected by finding users who use both BoardGameGeek (BGG) and Steam, and collating their game preferences from both platforms
    - You can download the dataset and read more about how it was made on the Dataset page 

- Questions? Ideas? Job? Contact me and say hello!
    - LinkedIn : [linked.com/brianwilliamsmith](https://www.linkedin.com/in/brian-william-smith/)
    - E-mail : bwsmith.linguist@gmail.com 

                ''')
