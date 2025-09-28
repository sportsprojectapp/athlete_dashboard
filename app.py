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
# Colors
# -------------------------------
bg_color = "#111111" if dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if dark_mode else "#000000"

# -------------------------------
# Dashboard Title & KPIs
# -------------------------------
st.markdown(f"<h1 style='color:{text_color}'>🏅 SAI-Assess — Athlete Dashboard</h1>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Athletes", len(df))
col2.metric("Average Score", round(df["score"].mean(),1))
col3.metric("Verified Athletes", int(df["verified"].sum()))
col4.metric("Unique Sports", df["sport"].nunique())
col5.metric("Age Range", f"{df['age'].min()}–{df['age'].max()}")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filter Athletes")
sport = st.sidebar.multiselect("Sport", options=sorted(df["sport"].unique()), default=sorted(df["sport"].unique()))
state = st.sidebar.multiselect("State", options=sorted(df["state"].unique()), default=sorted(df["state"].unique()))
age_range = st.sidebar.slider("Age range", 14, 30, (14,30))

filtered = df[(df["sport"].isin(sport)) & 
              (df["state"].isin(state)) & 
              (df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

# -------------------------------
# Layout: Left (charts) & Right (leaderboard)
# -------------------------------
left, right = st.columns([3,1])

with left:
    st.subheader("Score Distribution")
    if not filtered.empty:
        fig = px.histogram(filtered, x="score", nbins=12, color="gender", barmode="overlay", 
                           title="Scores by Gender", marginal="box", hover_data=filtered.columns,
                           template="plotly_dark" if dark_mode else "plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No score data to show.")

    st.subheader("Average Score by State")
    if not filtered.empty:
        state_avg = filtered.groupby("state", as_index=False)["score"].mean().sort_values("score", ascending=False)
        fig2 = px.bar(state_avg, x="state", y="score", color="score", color_continuous_scale="Viridis", 
                      title="Avg Score by State", text_auto=".2f",
                      template="plotly_dark" if dark_mode else "plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Score Heatmap by State & Sport")
    if not filtered.empty:
        heatmap_data = filtered.groupby(["state","sport"], as_index=False)["score"].mean()
        fig3 = px.density_heatmap(heatmap_data, x="sport", y="state", z="score", color_continuous_scale="Viridis",
                                  title="Average Score Heatmap",
                                  template="plotly_dark" if dark_mode else "plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Athlete Locations")
    if {"lat","lon"}.issubset(filtered.columns):
        fig_map = px.scatter_mapbox(filtered, lat="lat", lon="lon", hover_name="name", hover_data=["sport","score"],
                                    color="score", size="score", color_continuous_scale="Viridis", zoom=3, height=400)
        fig_map.update_layout(mapbox_style="carto-darkmatter" if dark_mode else "open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Latitude/Longitude data not available.")

with right:
    st.subheader("Top 10 Athletes")
    if not filtered.empty:
        top10 = filtered.sort_values("score", ascending=False).head(10)[["athlete_id","name","sport","state","score","date"]]
        st.dataframe(top10.reset_index(drop=True))
        csv = top10.to_csv(index=False).encode("utf-8")
        st.download_button("Download Top 10 CSV", data=csv, file_name="top10.csv", mime="text/csv")
    else:
        st.info("No athletes to show.")

# -------------------------------
# Athlete Drill-down & Comparison (Professional Layout)
# -------------------------------
st.markdown("---")
st.subheader("Athlete Profile Drill-down")

athlete_selection = st.multiselect("Select Athlete(s) for comparison", options=df["athlete_id"].tolist(), default=[df["athlete_id"].iloc[0]])

for aid in athlete_selection:
    profile = df[df["athlete_id"]==aid].iloc[0].to_dict()
    
    # Title
    st.markdown(f"### {profile['name']} — {profile['sport']}")
    
    # Layout: Photo + Details Table + Metrics
    cols = st.columns([1,2])
    
    # Photo

