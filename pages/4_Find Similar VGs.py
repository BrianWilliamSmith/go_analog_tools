import streamlit as st
from src.go_analog_shared_functions import *

st.title('🎲 Find the most similar games 🕹')
st.header('video games ⮕ video games')
st.write("Go Analog won't usually recommend games you own, but it sometimes recommends games you've played fewer than 10 minutes, and different versions of your games.")

find_similar('steam')
