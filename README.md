# UserInsight AI

UserInsight AI is a full-stack behaviour analytics platform. Authenticated users receive a unique tracking snippet (`<script src="https://your-domain/track.js?uid={USER_ID}"></script>`) that streams page views, clicks, scroll depth, and metadata to the FastAPI backend. Events are sessionised, enriched with metrics, and scored with a HuggingFace-hosted IsolationForest model so the React dashboard can surface summaries, charts, session drill-downs, anomalies, and file-uploaded datasets.

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables (see `backend/env.sample`) include:

- `MONGO_URI`, `MONGO_DB`
- `HF_MODEL_REPO`, `HF_MODEL_FILENAME`, `HF_TOKEN`
- `SESSION_IDLE_MINUTES`, `ANOMALY_SCORE_THRESHOLD`
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXP_MINUTES`
- `TRACKING_BASE_URL` (origin serving `/track.js` and `/collect`)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to the FastAPI origin (defaults to `http://localhost:8000`). The frontend bundles authentication pages, dashboard, upload workflow, and tracking-script instructions.

### Docker

`docker-compose up --build` launches MongoDB, the FastAPI API (port 8000), and the nginx-hosted frontend (port 5173).

## Key directories

- `backend/app/api` – auth, tracking, analytics, and upload routers
- `backend/app/services` – auth helpers, analytics/session processors, ML helpers
- `backend/app/schemas` – Pydantic DTOs shared across routes
- `frontend/src/pages` – login/signup/dashboard/upload/tracking pages
- `frontend/src/components` – layout, tables, charts, and drill-down widgets
- `frontend/src/services` – Axios clients for auth + analytics
- `frontend/src/hooks` – global auth context/provider

## Tests

`pytest backend/tests` validates backend utilities, and `npm run build` ensures the frontend compiles (add Vitest suites as needed).
