
# SAI-Assess Dashboard — Starter kit

This folder contains a starter Streamlit dashboard to visualize athlete assessment data (sample CSV included).
Files:
- `app.py` — Streamlit dashboard (reads `sample_athletes.csv` by default; optional Firestore integration if `USE_FIRESTORE=1` and `FIRESTORE_SERVICE_ACCOUNT` env var is set)
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container image for Cloud Run / Render
- `sample_athletes.csv` — Example data you can edit

## Quick local run
```bash
python -m venv venv
source venv/bin/activate   # on Windows: venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy options (short)
1. **Quick (free)**: Push repo to GitHub and deploy on **Streamlit Community Cloud** (one-click). See Streamlit docs: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app.  
2. **Production (recommended for uptime)**: Use **Google Cloud Run** (containerize with Dockerfile) and map a custom domain. See Cloud Run quickstart: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-streamlit-service. Cloud Run SLA: https://cloud.google.com/run/sla.  
3. **Alternative hosts**: Render.com can also host Streamlit apps (simple).

## Firestore integration
- To use Firestore, create a Firebase service account JSON and set it as the environment variable `FIRESTORE_SERVICE_ACCOUNT` (the app expects the JSON string). Also set `USE_FIRESTORE=1`.
- For production, store the service account JSON securely (e.g., Google Secret Manager or Streamlit Secrets).

## Next steps I can help with
- Customize dashboard charts (maps, heatmaps, policy dashboard)
- Prepare GitHub repo and CI/CD configuration
- Write Cloud Run deploy commands or GitHub Actions workflow
