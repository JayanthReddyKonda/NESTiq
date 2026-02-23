# SpaceForge 🏠

**AI-powered interior design & augmented-reality furniture placement.**

---

## Architecture

```
┌───────────────────────────────────────────────────────┐
│  Browser / Mobile                                      │
│  React + Vite + TypeScript                            │
│  React Three Fiber (3D)  │  model-viewer (AR/WebXR)  │
└─────────────────┬─────────────────────────────────────┘
                  │ HTTPS (ngrok static domain)
┌─────────────────▼─────────────────────────────────────┐
│  FastAPI (Python 3.11, async, Pydantic v2)            │
│  • /api/rooms/analyze          POST                   │
│  • /api/designs/generate       POST                   │
│  • /api/designs/render         POST (async job)       │
│  • /api/designs/render/{id}    GET  (poll)            │
│  • /api/ar/session/{id}        GET                    │
│  • /api/agent/procure          POST (SSE stream)      │
│  • /health                     GET                    │
│  • /static/*                   static file serving    │
│  • /*                          SPA catch-all          │
│                                                       │
│  SQLite (aiosqlite)  │  In-memory render queue        │
│  AI Provider abstraction → FakeProvider (default)     │
└───────────────────────────────────────────────────────┘
                  │
┌─────────────────▼─────────────────────────────────────┐
│  ngrok container   (optional --profile ngrok)         │
│  HTTPS tunnel → backend:8000                          │
└───────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker ≥ 24 with Compose v2
- (Optional) ngrok account for HTTPS tunnel

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env — defaults work for local dev
```

### 2. Run — backend + frontend together

```bash
docker compose -f docker-compose.yml -f docker-compose.frontend.yml up --build
```

| Service | URL |
|---------|-----|
| Frontend | <http://localhost:4173> |
| Backend API | <http://localhost:8000> |
| API docs | <http://localhost:8000/docs> *(requires `DEBUG=true` in `.env`)* |
| ngrok inspector | <http://localhost:4040> (if profile active) |

> **API docs are disabled by default** (production hardening).  
> Set `DEBUG=true` in your `.env` to enable `/docs`, `/redoc`, and `/openapi.json`.

### 2a. Backend only (API without UI)

```bash
docker compose up --build
```

### 2b. Frontend only (against a running backend)

```bash
# Point at whatever backend you already have running
BACKEND_PUBLIC_URL=http://localhost:8000 \
  docker compose -f docker-compose.frontend.yml up --build
```

### 3. Run with ngrok (HTTPS, mobile AR)

```bash
# .env
NGROK_AUTHTOKEN=xxxx
NGROK_DOMAIN=your-slug.ngrok-free.app
BACKEND_PUBLIC_URL=https://your-slug.ngrok-free.app

docker compose -f docker-compose.yml \
               -f docker-compose.frontend.yml \
               --profile ngrok up --build
```

Point your browser / mobile to `https://your-slug.ngrok-free.app`.

---

## Environment Configuration

All runtime configuration is driven by a single `.env` file. No values are hardcoded.

```bash
cp .env.example .env   # required before any docker compose command
```

### Variable tiers

| Tier | Meaning |
|------|---------|
| **REQUIRED** | No default — app refuses to start if unset |
| **RECOMMENDED** | Has a safe default but must be changed in production |
| **OPTIONAL** | Default is production-safe; change only if needed |

### Key variables

| Variable | Tier | Notes |
|----------|------|-------|
| `BACKEND_PUBLIC_URL` | REQUIRED | Full URL including scheme — used in all asset URLs returned by the API |
| `DATABASE_URL` | REQUIRED | Docker-compose overrides this to the volume path automatically |
| `SECRET_KEY` | RECOMMENDED | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALLOWED_ORIGINS` | RECOMMENDED | Set to your frontend URL(s) in production; `*` is fine for local dev |
| `DEBUG` | OPTIONAL | `true` enables `/docs`, `/redoc`, verbose logging. **Never `true` in production.** |
| `AI_PROVIDER` | OPTIONAL | `fake` (no keys needed) \| `openai` \| `replicate` |
| `OPENAI_API_KEY` | REQUIRED if `AI_PROVIDER=openai` | Stored as `SecretStr` — never appears in logs |
| `NGROK_AUTHTOKEN` | REQUIRED for `--profile ngrok` | From <https://dashboard.ngrok.com/get-started/your-authtoken> |

### Secrets in logs

All secret fields (`SECRET_KEY`, `OPENAI_API_KEY`, `REPLICATE_API_TOKEN`) are `SecretStr` — Pydantic redacts them automatically.  
Startup logs use `settings.safe_dump()` which explicitly replaces secrets with `[REDACTED]`.

---

## Folder Structure

```
├── backend/
│   └── ...                     (FastAPI, routers, services)
├── frontend/
│   └── ...                     (React + Vite)
├── docker-compose.yml           # Backend + ngrok
├── docker-compose.frontend.yml  # Frontend (portable, independent)
├── .env.example
└── README.md
```

---

## API Reference

All endpoints return JSON. Error responses follow FastAPI's default `{"detail": "..."}` format.

### `POST /api/rooms/analyze`

Upload a room photo and receive structured analysis.

**Request:** `multipart/form-data`  — `file`: image (JPEG/PNG/WEBP)  
**Response:** `RoomAnalyzeResponse` — `room_id`, `analysis` (dimensions, room_type, lighting, style_hints…)

---

### `POST /api/designs/generate`

Generate a furniture design for an analysed room.

**Body:**

```json
{ "room_id": "...", "style": "modern", "preferences": {} }
```

**Response:** `DesignGenerateResponse` — `design_id`, `furniture[]`, `color_palette`, `estimated_cost_usd`

---

### `POST /api/designs/render`

Submit an async SDXL render job.

**Body:** `{ "design_id": "..." }`  
**Response:** `RenderJobResponse` — `job_id`, `status: pending`

---

### `GET /api/designs/render/{job_id}`

Poll render job status.

**Response:** `RenderJobResponse` — `status: pending | processing | done | failed`, `image_url`

---

### `GET /api/ar/session/{design_id}`

Fetch AR session data (model URL + furniture positions).

**Response:**

```json
{
  "design_id": "...",
  "model_url": "https://.../static/models/room_default.glb",
  "positions": [{ "furniture_id": "...", "x": 0, "y": 0, "z": 1, "rotation_y": 0 }],
  "scale_factor": 1.0,
  "ar_modes": "webxr scene-viewer quick-look"
}
```

---

### `POST /api/agent/procure`

Stream procurement agent events via Server-Sent Events.

**Body:** `{ "design_id": "...", "budget_usd": 2000 }`  
**Response:** `text/event-stream`  
Events: `thought` | `action` | `result` | `summary` | `error` | `done`

---

## Production Checklist

Items marked `# TODO: PRODUCTION` in source:

| File | Item |
|------|------|
| `services/ai_provider.py` | Replace FakeProvider with GPT-4V + SDXL (Replicate/Modal) |
| `services/ai_provider.py` | Implement OpenAIProvider fully — use `.get_secret_value()` on `SecretStr` fields |
| `services/render_queue.py` | Replace in-memory queue with Celery + Redis or ARQ |
| `routers/ar.py` | Generate per-design GLTF/GLB from furniture layout |
| `components/ARPage.tsx` | Serve real USDZ for iOS Quick Look |
| `.env` / infra | Migrate secrets to Vault / AWS Secrets Manager / Doppler for prod deployments |
| `.env` | Set `ALLOWED_ORIGINS` to exact frontend URL(s) — remove wildcard |
| `.env` | Set `DATABASE_URL` to PostgreSQL DSN for production |

---

## Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173 (proxies /api to localhost:8000)
```
