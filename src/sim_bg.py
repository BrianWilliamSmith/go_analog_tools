import streamlit as st
import sim

def app():
    st.title('Find the most similar games')
    st.header('video games ⮕ board games')
    sim.find_similar('bgg')