import streamlit as st
import pandas as pd
from src import home, sim_bg, sim_vg, dataset, go_analog, how

def main():
    st.set_page_config(page_title='Go Analog', page_icon=':game_die:')
    st.sidebar.title("Go Analog: board game and video game tools")
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    page = pages.get(selection)
    page.app()

pages = {
    "Home": home,
    "Go Analog: Recommend BGs based on your Steam profile": go_analog,
    "Convert VG ⮕ BG": sim_bg,
    "Convert VG ⮕ VG": sim_vg,
    "Dataset": dataset,
    "How's it work?": how
    }

if __name__ == "__main__":
    main()
    