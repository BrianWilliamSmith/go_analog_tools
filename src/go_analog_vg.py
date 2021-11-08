import streamlit as st
from src.go_analog_shared_functions import *

def app():

    st.title('🎲 Go Analog 🕹')
    st.header('recommend video games based on your Steam profile')

    go_analog_app(platform = 'steam')

