# Lead Intelligence — SaaSquatch Enhancement

Built for Caprae Capital's Full Stack Developer AI-Readiness Challenge.

A companion tool to [SaaSquatch Leads](https://www.saasquatchleads.com/) that takes raw scraped
lead data and adds three things SaaSquatch's core scraper doesn't do transparently: **deduplication**,
**data validation**, and **explainable AI-powered lead scoring** — so a sales rep opens their CSV
already knowing which 10 leads to call first, and why.

## Why this feature

SaaSquatch scrapes companies at volume and shows an "AI Company Score," but reps still have to
manually sift through hundreds of rows, duplicate entries from re-scraping the same company, and
sometimes-invalid emails, before they can prioritize outreach. This tool sits on top of that raw
output and turns a spreadsheet into a ranked, explained shortlist — directly addressing the
"prioritize high-impact leads, minimize irrelevant data" evaluation criterion.

## Architecture
┌─────────────────┐ ┌──────────────────┐ ┌─────────────┐
│ Next.js (TS) │ REST │ FastAPI │ SQL │ SQLite │
│ Vercel │────────▶│ Render │───────▶│ (leads.db) │
│ Dashboard UI │◀────────│ Validation/Dedup │◀───────│ │
└─────────────────┘ │ Scoring (Gemini) │ └─────────────┘
└──────────────────┘


**Backend — FastAPI + SQLite + SQLAlchemy**
- SQLite chosen deliberately for this scope: zero-config, no external service to spin up, and fast
  for the thousands-of-leads range a single sales rep or small team works with. The SQLAlchemy
  models are written so a swap to managed Postgres (the production choice past ~100k rows or
  multiple concurrent writers) requires changing one connection string, not the schema or queries.
- **Validation** (`app/services/validation.py`): regex-based email/phone checks. Deliberately simple
  and fast — this is a first-pass filter, not a full deliverability check (that would need an SMTP
  ping or a paid verification API, which is a reasonable v2).
- **Dedup** (`app/services/dedup.py`): fuzzy matching via `rapidfuzz`. Domain match is the strongest
  signal (same website scraped twice); company-name similarity (`token_sort_ratio` ≥ 90) catches
  "Acme Inc" vs "Acme Incorporated" without a hard-coded name list.
- **Scoring** (`app/services/scoring.py`): a *hybrid* approach on purpose. A deterministic rule-based
  score (log-scaled revenue + employees + source confidence + data completeness) is the anchor a
  sales manager could verify by hand. Gemini is then asked to review that score and nudge it by at
  most ±10 points if it spots a qualitative signal the formula can't see (industry fit, ICP match) —
  and to write a one-sentence, sales-ready justification. This avoids the common failure mode of
  "the AI just made up a number": the score is always explainable and bounded. If no `GEMINI_API_KEY`
  is set, the tool still works end-to-end on the rule-based score alone.
- Caching/perf: for this data volume, no dedicated cache layer was needed — SQLite reads for a table
  of a few thousand rows are sub-millisecond. If this scaled to millions of leads, the obvious next
  step is a Redis cache in front of the `/leads` list endpoint and moving scoring to a background
  queue (Celery/RQ) rather than the synchronous `/leads/score` call used here.

**Frontend — Next.js 16 (App Router, TypeScript) + Tailwind v4**
- TanStack Query handles all server state (loading/error states, cache invalidation on
  upload/score) instead of manual `useState`/`useEffect` fetch juggling.
- UX intent: dense, single-table "ops desk" view rather than a card grid — a rep scanning 50+ leads
  wants a sortable, scannable list, not scrolling through cards. Tier is shown as both a color dot
  and the score itself, so filtering by "Hot" and reading the AI's one-line reasoning both happen in
  the same glance.
- Design tokens are deliberately not the default "AI generated" look: a charcoal ops-desk palette
  (`#14171C` background) with rust/teal/slate tier colors instead of generic card shadows, and a
  monospace type treatment for all numeric data so scores line up and never jitter.

## Tech stack

| Layer | Choice |
|---|---|
| Backend framework | FastAPI |
| Database | SQLite (SQLAlchemy ORM) |
| Dedup | rapidfuzz |
| AI scoring | Google Gemini API (`gemini-1.5-flash`) |
| Frontend framework | Next.js 16 (App Router, TypeScript) |
| Styling | Tailwind CSS v4 |
| Data fetching | TanStack Query + Axios |
| Frontend hosting | Vercel (static/serverless) |
| Backend hosting | Render (native Python web service) |

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
# copy .env.example to .env and add your GEMINI_API_KEY (optional -- works without it)
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
# copy .env.local.example to .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

### Try it

1. Open `http://localhost:3000`
2. Click **Upload leads CSV** and select `data/sample_raw_leads.csv` (15 sample leads with
   intentional duplicates and bad data, simulating raw scraper output)
3. Click **Run AI scoring**
4. Filter by tier, sort by score, export the ranked list to CSV

## Deployment

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for step-by-step Render + Vercel deployment instructions.

## Project structure
saasquatch-lead-intelligence/
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI app, CORS, router registration
│ │ ├── database.py # SQLAlchemy engine/session
│ │ ├── schemas.py # Pydantic response models
│ │ ├── models/lead.py # Lead table schema
│ │ ├── services/
│ │ │ ├── validation.py # Email/phone regex validation
│ │ │ ├── dedup.py # Fuzzy duplicate detection
│ │ │ └── scoring.py # Rule-based + Gemini AI scoring
│ │ └── routers/leads.py # /leads/* endpoints
│ ├── requirements.txt
│ └── .env.example
├── frontend/
│ ├── src/
│ │ ├── app/ # Next.js App Router pages/layout
│ │ ├── components/ # ControlPanel, FilterBar, StatsStrip, LeadsTable
│ │ └── lib/api.ts # Typed API client
│ └── .env.local.example
├── data/
│ └── sample_raw_leads.csv # Demo dataset with intentional dupes/bad data
└── README.md