import streamlit as st
from src.sim import *

def app():
    st.title('Find the most similar games')
    st.header('video games ⮕ board games')
    find_similar('bgg')