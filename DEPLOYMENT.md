# DocQuery — Deployment Guide

DocQuery has two parts:

| Part | Deployed where | Notes |
|---|---|---|
| **Frontend** (Next.js) | GitHub Pages (auto via CI) | Static export — no server needed |
| **Backend** (FastAPI + ChromaDB) | Render.com free tier | Auto-seeds VaultPay demo docs on cold start |

---

## 1. Deploy the backend to Render

### Prerequisites
- A [Render.com](https://render.com) account (free)
- Your OpenAI API key

### Steps

1. Go to **https://render.com** → **New** → **Web Service**
2. Connect your GitHub account and select the `SulagnaSasmal/docquery` repo
3. Render will detect `render.yaml` automatically. Accept the defaults.
4. In **Environment Variables**, set:
   - `OPENAI_API_KEY` → your key (e.g. `sk-…`)
5. Click **Deploy**

Render will:
- Install Python dependencies (`pip install -r requirements.txt`)
- Start the FastAPI server
- On first startup, auto-crawl the VaultPay API docs and index them into ChromaDB (~15–30 seconds)

Your backend URL will be: **`https://docquery-api.onrender.com`**

> **Free tier note:** The service sleeps after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up + re-seed. This is normal for a demo.

---

## 2. Connect the frontend to the backend

After Render gives you a live URL, tell GitHub Actions where to find it:

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Variables**
2. Click **New repository variable**
3. Name: `DOCQUERY_API_URL`
4. Value: `https://docquery-api.onrender.com` (or whatever Render gives you)
5. Save

6. In GitHub Actions → **Actions** tab → **Deploy to GitHub Pages** → click **Re-run all jobs**

The frontend will rebuild with the correct `NEXT_PUBLIC_API_URL` baked in. The live chat will now call your Render backend.

---

## 3. Verify it works

Open `https://sulagnasasmal.github.io/docquery/` and ask:

> *"How does OAuth authentication work?"*

You should see an answer with citations pointing to the VaultPay API docs.

---

## Local development

```bash
# Clone the repo
git clone https://github.com/SulagnaSasmal/docquery
cd docquery

# Copy env and fill in your OpenAI key
cp .env.example .env

# Install backend
pip install -r requirements.txt

# Start backend (port 8000)
uvicorn api.main:app --reload

# In a second terminal — start frontend
cd frontend
npm install
npm run dev
```

---

## Seeded demo collections

On startup (when `AUTO_SEED=true`), the backend indexes:

| Collection name | Source |
|---|---|
| `vaultpay` | https://sulagnasasmal.github.io/vaultpay-api-docs/ |

To add more collections, edit `ingestion/seed.py` → `DEMO_COLLECTIONS`.
