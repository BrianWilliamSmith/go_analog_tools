import streamlit as st
import pandas as pd
from src import home
from src import sim_bg 
from src import sim_vg
from src import dataset
from src import go_analog_bg
from src import go_analog_vg
from src import how_it_works

def main():

    st.set_page_config(page_title='Go Analog', page_icon=':game_die:')

    st.sidebar.title("Go Analog: board game and video game tools")

    selection = st.sidebar.radio("Go to", list(pages.keys()))

    page = pages.get(selection)
    page.app()

pages = {
    "Home": home,
    "Go Analog: VG ⮕ BG": go_analog_bg,
    "Go Analog: VG ⮕ VG": go_analog_vg,
    "Convert VG ⮕ BG": sim_bg,
    "Convert VG ⮕ VG": sim_vg,
    "Dataset": dataset,
    "How's it work?": how_it_works
    }

if __name__ == "__main__":
    main()