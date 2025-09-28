import os, json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

# -------------------------------
# Theme toggle
# -------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

st.sidebar.header("Dashboard Theme")
theme_choice = st.sidebar.radio("Choose Theme", ["Light","Dark"], index=0 if st.session_state.theme=="light" else 1)
st.session_state.theme = theme_choice.lower()
dark_mode = st.session_state.theme == "dark"

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="SAI-Assess Dashboard", layout="wide", page_icon="🏃‍♂️")

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

    sample_videos = [
        "https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"
    ] * 10

    sample_photos = [
        f"https://randomuser.me/api/portraits/men/{i}.jpg" if i % 2 == 0 else
        f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(20)
    ]

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
            "date": datetime(2025, random.randint(7,9), random.randint(10,20)),
            "verified": random.choice([True, False]),
            "video_url": video_url,
            "photo_url": sample_photos[i]
        }
        sample.append(athlete)
    pd.DataFrame(sample).to_csv("sample_athletes.csv", index=False)
    df = pd.DataFrame(sample)
    df["video_url"] = df["video_url"].fillna("")
    df["photo_url"] = df["photo_url"].fillna("")
    return df

# -------------------------------
# Firestore loader
# -------------------------------
def load_firestore():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not os.environ.get("FIRESTORE_SERVICE_ACCOUNT"):
            st.warning("Firestore not configured. Using local CSV data.")
            return load_local_csv()
        sa = json.loads(os.environ["FIRESTORE_SERVICE_ACCOUNT"])
        if not firebase_admin._apps:
            cred = credentials.Certificate(sa)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        docs = db.collection("athletes").stream()
        rows = [d.to_dict() for d in docs]
        df = pd.DataFrame(rows)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        if "video_url" in df.columns:
            df["video_url"] = df["video_url"].fillna("")
        if "photo_url" in df.columns:
            df["photo_url"] = df["photo_url"].fillna("")
        return df
    except Exception as e:
        st.error(f"Firestore load failed: {e}. Falling back to CSV.")
        return load_local_csv()

# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_data():
    if os.environ.get("USE_FIRESTORE") == "1":
        return load_firestore()
    return load_local_csv()

df = load_data()

# -------------------------------
# Dashboard Title & KPIs
# -------------------------------
bg_color = "#_
