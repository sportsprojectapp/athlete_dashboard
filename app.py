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
        .css-1d391kg, .css-1v3fvcr {{
            background-color: {bg};
        }}
    </style>
    """, unsafe_allow_html=True)
apply_theme(dark_mode)

# -------------------------------
# Sample data generator
# -------------------------------
@st.cache_data
def load_local_csv():
    sports = ["Sprinting", "Long Jump", "High Jump", "Shot Put", "Javelin", 
              "Discus", "Swimming", "Cycling", "Gymnastics", "Wrestling"]
    states = ["Kerala", "Kerala", "Kerala", "Kerala", "Kerala", 
              "Karnataka", "Maharashtra", "Tamil Nadu", "Punjab", "Uttar Pradesh",
              "Bihar", "Rajasthan", "Goa", "Delhi", "Haryana", 
              "Gujarat", "Madhya Pradesh", "Odisha", "Assam", "West Bengal"]
    sample_videos = ["https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"]*10
    sample_photos = [f"https://randomuser.me/api/portraits/men/{i}.jpg" if i % 2 == 0 else f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(20)]
    sample = []
    for i in range(20):
        video_url = sample_videos[i] if i < 10 else ""
        athlete = {
            "athlete_id": f"A{str(i+1).zfill(3)}",
            "name": f"Athlete_{i+1}",
            "age": random.randint(14,30),
            "gender": random.choice(["M","F"]),
            "sport": sports[i % len(sports)],
            "state": states[i],
            "score": random.randint(60,95),
            "lat": round(random.uniform(8.5,30.9),4),
            "lon": round(random.uniform(75.0,80.5),4),
            "date": dat




