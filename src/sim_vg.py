import streamlit as st
import sim

def app():
    st.title('Find the most similar games')
    st.header('video games ⮕ video games')
    sim.find_similar('steam')
