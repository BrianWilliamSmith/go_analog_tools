import streamlit as st
from src.go_analog_shared_functions import *

def app():

    st.title('🎲 Find the most similar games 🕹')

    st.header('video games ⮕ board games')
    
    find_similar('bgg')