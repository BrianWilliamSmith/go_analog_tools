import streamlit as st
from src.go_analog_shared_functions import *

def app():

    st.title('🎲 Go Analog 🕹')
    st.header('recommend board games based on your Steam profile')

    go_analog_app(platform = 'bgg')

