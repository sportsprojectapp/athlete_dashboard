
import os, json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="SAI-Assess Dashboard", layout="wide")

@st.cache_data
def load_local_csv():
    if not os.path.exists("sample_athletes.csv"):
        sample = [
            {"athlete_id":"A001","name":"Raj","age":16,"gender":"M","sport":"Sprinting","state":"Uttar Pradesh","score":78,"lat":26.8467,"lon":80.9462,"date":"2025-07-10","verified":True},
            {"athlete_id":"A002","name":"Priya","age":15,"gender":"F","sport":"Long Jump","state":"Karnataka","score":84,"lat":12.9716,"lon":77.5946,"date":"2025-07-12","verified":True},
            {"athlete_id":"A003","name":"Rahul","age":17,"gender":"M","sport":"High Jump","state":"Maharashtra","score":69,"lat":19.0760,"lon":72.8777,"date":"2025-07-11","verified":False},
            {"athlete_id":"A004","name":"Anita","age":14,"gender":"F","sport":"Sprinting","state":"Tamil Nadu","score":91,"lat":13.0827,"lon":80.2707,"date":"2025-07-13","verified":True},
            {"athlete_id":"A005","name":"Sunil","age":18,"gender":"M","sport":"Long Jump","state":"Punjab","score":72,"lat":31.1471,"lon":75.3412,"date":"2025-07-14","verified":False}
        ]
        pd.DataFrame(sample).to_csv("sample_athletes.csv", index=False)
    return pd.read_csv("sample_athletes.csv", parse_dates=["date"])

def load_firestore():
    # Optional: read from Firestore if you set environment variables
    # Set USE_FIRESTORE=1 and FIRESTORE_SERVICE_ACCOUNT (JSON string)
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not os.environ.get("FIRESTORE_SERVICE_ACCOUNT"):
            st.error("Environment variable FIRESTORE_SERVICE_ACCOUNT not set. Falling back to sample CSV.")
            return load_local_csv()
        sa = json.loads(os.environ["FIRESTORE_SERVICE_ACCOUNT"])
        if not firebase_admin._apps:
            cred = credentials.Certificate(sa)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        docs = db.collection("athletes").stream()
        rows = [d.to_dict() for d in docs]
        if not rows:
            st.warning("No documents found in Firestore collection 'athletes'.")
            return pd.DataFrame(rows)
        df = pd.DataFrame(rows)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Failed to load Firestore data: {e}")
        return load_local_csv()

@st.cache_data
def load_data():
    if os.environ.get("USE_FIRESTORE") == "1":
        return load_firestore()
    else:
        return load_local_csv()

df = load_data()

st.title("SAI-Assess — Athlete Dashboard")

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Athletes", len(df))
col2.metric("Avg Score", round(df["score"].mean(),1) if "score" in df.columns else "—")
col3.metric("Verified", int(df["verified"].sum()) if "verified" in df.columns else "—")
col4.metric("Unique Sports", df["sport"].nunique() if "sport" in df.columns else "—")

# Sidebar filters
st.sidebar.header("Filters")
sport = st.sidebar.multiselect("Sport", options=sorted(df["sport"].unique().tolist()) if "sport" in df.columns else [], default=None)
state = st.sidebar.multiselect("State", options=sorted(df["state"].unique().tolist()) if "state" in df.columns else [], default=None)
age = st.sidebar.slider("Age range", int(df["age"].min()), int(df["age"].max()), (int(df["age"].min()), int(df["age"].max()))) if "age" in df.columns else None

# Apply filters
filtered = df.copy()
if sport:
    filtered = filtered[filtered["sport"].isin(sport)]
if state:
    filtered = filtered[filtered["state"].isin(state)]
if age is not None and "age" in df.columns:
    filtered = filtered[(filtered["age"]>=age[0]) & (filtered["age"]<=age[1])]

# Layout: left (charts) and right (leaderboard)
left, right = st.columns([3,1])

with left:
    st.subheader("Score distribution")
    if not filtered.empty and "score" in filtered.columns:
        fig = px.histogram(filtered, x="score", nbins=10, title="Scores distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No score data to show.")

    st.subheader("Average score by state")
    if "state" in filtered.columns and "score" in filtered.columns:
        state_avg = filtered.groupby("state", as_index=False)["score"].mean().sort_values("score", ascending=False)
        fig2 = px.bar(state_avg, x="state", y="score", title="Avg score by state")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Map of athletes (lat/lon required)")
    if {"lat","lon"}.issubset(filtered.columns):
        st.map(filtered.rename(columns={"lat":"lat","lon":"lon"})[["lat","lon"]])
    else:
        st.info("Latitude/Longitude columns (lat, lon) not found in data.")

with right:
    st.subheader("Top athletes")
    if not filtered.empty and "score" in filtered.columns:
        top = filtered.sort_values("score", ascending=False).head(10)[["athlete_id","name","sport","state","score","date"]]
        st.dataframe(top.reset_index(drop=True))
        csv = top.to_csv(index=False).encode('utf-8')
        st.download_button("Download top-10 CSV", data=csv, file_name="top10.csv", mime="text/csv")
    else:
        st.info("No athletes to show.")

st.markdown("---")
st.subheader("Athlete profile drill-down")
if not df.empty:
    aid = st.selectbox("Pick athlete", options=df["athlete_id"].tolist())
    profile = df[df["athlete_id"]==aid].iloc[0].to_dict()
    st.json(profile)
    if "video_url" in df.columns and profile.get("video_url"):
        st.video(profile.get("video_url"))
else:
    st.info("Dataset empty. Add sample_athletes.csv or connect Firestore.")

st.caption("This is a starter dashboard. Connect your real data (Firestore or CSV) and deploy to Streamlit Cloud / Cloud Run.")

