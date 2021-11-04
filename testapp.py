import streamlit as st
import pandas as pd
from src import home, sim_bg, sim_vg, go_analog

def main():
    st.sidebar.title("Tools")
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    page = pages.get(selection)
    page.app()

pages = {
    "Home": home,
    "Steam games to BGs": go_analog,
    "VG ⮕ BG": sim_bg,
    "VG ⮕ VG": sim_vg
    }

if __name__ == "__main__":
    main()
