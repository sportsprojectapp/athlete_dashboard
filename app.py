import os, json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="SAI-Assess Dashboard", layout="wide", page_icon="🏃‍♂️")

# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_local_csv():
    if not os.path.exists("sample_athletes.csv"):
        sample = [
            {"athlete_id":"A001","name":"Raj","age":16,"gender":"M","sport":"Sprinting","state":"Uttar Pradesh","score":78,"lat":26.8467,"lon":80.9462,"date":"2025-07-10","verified":True,"video_url":"https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"},
            {"athlete_id":"A002","name":"Priya","age":15,"gender":"F","sport":"Long Jump","state":"Karnataka","score":84,"lat":12.9716,"lon":77.5946,"date":"2025-07-12","verified":True,"video_url":"https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"},
            {"athlete_id":"A003","name":"Rahul","age":17,"gender":"M","sport":"High Jump","state":"Maharashtra","score":69,"lat":19.0760,"lon":72.8777,"date":"2025-07-11","verified":False,"video_url":""},
            {"athlete_id":"A004","name":"Anita","age":14,"gender":"F","sport":"Sprinting","state":"Tamil Nadu","score":91,"lat":13.0827,"lon":80.2707,"date":"2025-07-13","verified":True,"video_url":"https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"},
            {"athlete_id":"A005","name":"Sunil","age":18,"gender":"M","sport":"Long Jump","state":"Punjab","score":72,"lat":31.1471,"lon":75.3412,"date":"2025-07-14","verified":False,"video_url":""}
        ]
        pd.DataFrame(sample).to_csv("sample_athletes.csv", index=False)
    df = pd.read_csv("sample_athletes.csv", parse_dates=["date"])
    if "video_url" in df.columns:
        df["video_url"] = df["video_url"].fillna("")
    return df

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
        return df
    except Exception as e:
        st.error(f"Firestore load failed: {e}. Falling back to CSV.")
        return load_local_csv()

@st.cache_data
def load_data():
    if os.environ.get("USE_FIRESTORE") == "1":
        return load_firestore()
    return load_local_csv()

df = load_data()

# -------------------------------
# Dashboard Title & KPIs
# -------------------------------
st.title("🏅 SAI-Assess — Athlete Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Athletes", len(df))
col2.metric("Average Score", round(df["score"].mean(),1) if "score" in df.columns else "—")
col3.metric("Verified Athletes", int(df["verified"].sum()) if "verified" in df.columns else "—")
col4.metric("Unique Sports", df["sport"].nunique() if "sport" in df.columns else "—")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filter Athletes")
sport = st.sidebar.multiselect("Sport", options=sorted(df["sport"].unique()), default=sorted(df["sport"].unique()))
state = st.sidebar.multiselect("State", options=sorted(df["state"].unique()), default=sorted(df["state"].unique()))
age_range = st.sidebar.slider("Age range", int(df["age"].min()), int(df["age"].max()), (int(df["age"].min()), int(df["age"].max())))

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
        fig = px.histogram(filtered, x="score", nbins=10, color="gender", barmode="overlay", title="Scores by Gender")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No score data to show.")

    st.subheader("Average Score by State")
    if not filtered.empty:
        state_avg = filtered.groupby("state", as_index=False)["score"].mean().sort_values("score", ascending=False)
        fig2 = px.bar(state_avg, x="state", y="score", color="score", color_continuous_scale="Viridis", title="Avg Score by State")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Athlete Locations")
    if {"lat","lon"}.issubset(filtered.columns):
        st.map(filtered[["lat","lon"]])
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
# Athlete Drill-down
# -------------------------------
st.markdown("---")
st.subheader("Athlete Profile Drill-down")
if not df.empty:
    aid = st.selectbox("Select Athlete", options=df["athlete_id"].tolist())
    profile = df[df["athlete_id"]==aid].iloc[0].to_dict()
    st.json(profile)

    # Show video safely
    video_url = profile.get("video_url")
    if video_url and isinstance(video_url, str) and video_url.strip() != "":
        st.video(video_url)
    else:
        st.info("No video available for this athlete.")

# -------------------------------
st.caption("This dashboard is a starter template. Connect real Firestore or CSV data for full deployment.")


