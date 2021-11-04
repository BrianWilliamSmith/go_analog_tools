import streamlit as st
import sim

def app():
    st.title('Find similar: video -> board')
    sim.app('bgg')
