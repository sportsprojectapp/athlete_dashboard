import os, json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="SAI-Assess Dashboard", layout="wide", page_icon="🏃‍♂️")

# -------------------------------
# Sidebar theme toggle
# -------------------------------
st.sidebar.header("Theme & Filters")
dark_mode = st.sidebar.checkbox("Dark Mode", value=True)

def apply_theme(dark_mode=True):
    bg = "#111111" if dark_mode else "#FFFFFF"
    fg = "#FFFFFF" if dark_mode else "#000000"
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg};
            color: {fg};
        }}
        .stTable td, .stTable th {{
            color: {fg};
        }}
    </style>
    """, unsafe_allow_html=True)

apply_theme(dark_mode)

# -------------------------------
# Sample data generator
# -------------------------------
@st.cache_data
def load_local_csv():






