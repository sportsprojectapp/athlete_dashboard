
import os
import json
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

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
    sports = ["Sprinting", "Long Jump", "High Jump", "Shot Put", "Javelin",
              "Discus", "Swimming", "Cycling", "Gymnastics", "Wrestling"]
    states = ["Kerala", "Kerala", "Kerala", "Kerala", "Kerala",
              "Karnataka", "Maharashtra", "Tamil Nadu", "Punjab", "Uttar Pradesh",
              "Bihar", "Rajasthan", "Goa", "Delhi", "Haryana",
              "Gujarat", "Madhya Pradesh", "Odisha", "Assam", "West Bengal"]
    sample_videos = ["https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"]*10
    sample_photos = [f"https://randomuser.me/api/portraits/men/{i}.jpg" if i % 2 == 0
                     else f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(20)]

    sample = []
    for i in range(20):
        video_url = sample_videos[i] if i < 10 else ""
        athlete = {
            "athlete_id": f"A{str(i+1).zfill(3)}",
            "name": f"Athlete_{i+1}",
            "age": random.randint(14, 30),
            "gender": random.choice(["M", "F"]),
            "sport": sports[i % len(sports)],
            "state": states[i],
            "score": random.randint(60, 95),
            "lat": round(random.uniform(8.5, 30.9), 4),
            "lon": round(random.uniform(75.0, 80.5), 4),
            "date": datetime(2025, random.randint(7, 9), random.randint(10, 20)),
            "verified": random.choice([True, False]),
            "video_url": video_url,
            "photo_url": sample_photos[i]
        }
        sample.append(athlete)

    df = pd.DataFrame(sample)
    df["video_url"] = df["video_url"].fillna("")
    df["photo_url"] = df["photo_url"].fillna("")
    return df


# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_data():
    return load_local_csv()


df = load_data()

# -------------------------------
# Dashboard Title
# -------------------------------
text_color = "#FFFFFF" if dark_mode else "#000000"
st.markdown(f"<h1 style='color:{text_color}'>🏅 SAI-Assess — Athlete Dashboard</h1>", unsafe_allow_html=True)

# -------------------------------
# KPI cards
# -------------------------------
kpi_color = "#FFFFFF" if dark_mode else "#000000"
bg_color_card = "#333333" if dark_mode else "#DDDDDD"

col1, col2, col3, col4, col5 = st.columns(5)
kpis = [
    ("Total Athletes", len(df)),
    ("Average Score", round(df["score"].mean(), 1)),
    ("Verified Athletes", int(df["verified"].sum())),
    ("Unique Sports", df["sport"].nunique()),
    ("Age Range", f"{df['age'].min()}–{df['age'].max()}")
]

for c, (title, value) in zip([col1, col2, col3, col4, col5], kpis):
    c.markdown(f"""
    <div style="background-color:{bg_color_card}; padding:20px; border-radius:10px; text-align:center;">
        <h4 style="color:{kpi_color}; margin:0;">{title}</h4>
        <h2 style="color:{kpi_color}; margin:0;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Sidebar Filters
# -------------------------------
sport = st.sidebar.multiselect("Sport", options=sorted(df["sport"].unique()), default=sorted(df["sport"].unique()))
state = st.sidebar.multiselect("State", options=sorted(df["state"].unique()), default=sorted(df["state"].unique()))
age_range = st.sidebar.slider("Age range", 14, 30, (14, 30))

filtered = df[(df["sport"].isin(sport)) &
              (df["state"].isin(state)) &
              (df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

# -------------------------------
# Layout: Left (charts) & Right (leaderboard)
# -------------------------------
left, right = st.columns([3, 1])
template = "plotly_dark" if dark_mode else "plotly_white"

with left:
    st.subheader("Score Distribution")
    if not filtered.empty:
        fig = px.histogram(filtered, x="score", nbins=12, color="gender", barmode="overlay",
                           title="Scores by Gender", marginal="box", hover_data=filtered.columns,
                           template=template)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No score data to show.")

    st.subheader("Average Score by State")
    if not filtered.empty:
        state_avg = filtered.groupby("state", as_index=False)["score"].mean().sort_values("score", ascending=False)
        fig2 = px.bar(state_avg, x="state", y="score", color="score", color_continuous_scale="Viridis",
                      title="Avg Score by State", text_auto=".2f", template=template)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Score Heatmap by State & Sport")
    if not filtered.empty:
        heatmap_data = filtered.groupby(["state", "sport"], as_index=False)["score"].mean()
        fig3 = px.density_heatmap(heatmap_data, x="sport", y="state", z="score", color_continuous_scale="Viridis",
                                  title="Average Score Heatmap", template=template)
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Athlete Locations")
    if {"lat", "lon"}.issubset(filtered.columns):
        fig_map = px.scatter_mapbox(filtered, lat="lat", lon="lon", hover_name="name", hover_data=["sport", "score"],
                                    color="score", size="score", color_continuous_scale="Viridis", zoom=3, height=400)
        fig_map.update_layout(mapbox_style="carto-darkmatter" if dark_mode else "open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Latitude/Longitude data not available.")

with right:
    st.subheader("Top 10 Athletes")
    if not filtered.empty:
        top10 = filtered.sort_values("score", ascending=False).head(10)[["athlete_id", "name", "sport", "state", "score", "date"]]
        st.dataframe(top10.reset_index(drop=True))
        csv = top10.to_csv(index=False).encode("utf-8")
        st.download_button("Download Top 10 CSV", data=csv, file_name="top10.csv", mime="text/csv")
    else:
        st.info("No athletes to show.")

# -------------------------------
# Athlete Drill-down & Comparison
# -------------------------------
st.markdown("---")
st.subheader("Athlete Profile Drill-down")
athlete_selection = st.multiselect("Select Athlete(s) for comparison", options=df["athlete_id"].tolist(), default=[df["athlete_id"].iloc[0]])

for aid in athlete_selection:
    profile = df[df["athlete_id"] == aid].iloc[0].to_dict()
    st.markdown(f"### {profile['name']} — {profile['sport']}", unsafe_allow_html=True)

    cols = st.columns([1, 2])
    with cols[0]:
        st.image(profile.get("photo_url"), width=120)
    with cols[1]:
        detail_data = {
            "Attribute": ["Athlete ID", "Name", "Age", "Gender", "Sport", "State", "Date", "Verified"],
            "Value": [profile["athlete_id"], profile["name"], profile["age"], profile["gender"],
                      profile["sport"], profile["state"], profile["date"].strftime("%Y-%m-%d"),
                      "✅ Yes" if profile["verified"] else "❌ No"]
        }
        st.markdown(f"<div style='color:{text_color}'>", unsafe_allow_html=True)
        st.table(pd.DataFrame(detail_data))
        st.markdown("</div>", unsafe_allow_html=True)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Score", profile["score"])
    metric_cols[1].metric("Age", profile["age"])
    metric_cols[2].metric("Verified", "Yes" if profile["verified"] else "No")

    video_url = profile.get("video_url")
    if video_url and isinstance(video_url, str) and video_url.strip() != "":
        st.video(video_url)
    else:
        st.info("No video available for this athlete.")

st.caption("This dashboard is a professional starter template. Connect real Firestore or CSV data for full deployment.")






