# Deployment Guide

Backend → Render · Frontend → Vercel

## 1. Push to GitHub

```bash
# from the saasquatch-lead-intelligence/ root
git remote add origin https://github.com/<your-username>/saasquatch-lead-intelligence.git
git branch -M main
git push -u origin main
```

(Create the empty repo on GitHub first — github.com → New repository → don't initialize with a
README, since this local repo already has one.)

## 2. Deploy the backend on Render

1. Go to https://dashboard.render.com → **New +** → **Web Service**
2. Connect your GitHub repo, select this repo
3. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (Render dashboard → Environment):
   - `GEMINI_API_KEY` = your Gemini API key (optional — tool works without it)
   - `DATABASE_URL` = `sqlite:///./leads.db`
   - `CORS_ORIGINS` = your Vercel URL once you have it, e.g. `https://your-app.vercel.app`
5. Deploy. Note the resulting URL, e.g. `https://saasquatch-lead-intelligence.onrender.com`

**Note on SQLite on Render**: Render's filesystem is ephemeral on the free tier — the SQLite file
resets on redeploy. That's fine for a demo/assessment. For a persistent production deployment,
provision a Render Postgres instance and point `DATABASE_URL` at it instead; no code changes
needed beyond that env var, since SQLAlchemy handles both dialects.

## 3. Deploy the frontend on Vercel

1. Go to https://vercel.com/new
2. Import the same GitHub repo
3. Configure:
   - **Root Directory**: `frontend`
   - Framework preset: Next.js (auto-detected)
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render backend URL from step 2
5. Deploy

## 4. Connect the two

Go back to Render → your backend service → Environment → update `CORS_ORIGINS` to your live
Vercel URL, then trigger a redeploy so CORS allows requests from production frontend.

## 5. Verify

Visit your Vercel URL, upload `data/sample_raw_leads.csv`, click **Run AI scoring**, confirm leads
appear ranked and filterable.