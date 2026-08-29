# PRP: Vireel

> Implementation blueprint for parallel agent execution

---

## METADATA

| Field | Value |
|-------|-------|
| **Product** | Vireel |
| **Type** | SaaS |
| **Version** | 1.0 |
| **Created** | 2026-08-29 |
| **Complexity** | High (async media pipeline: yt-dlp + Whisper + GPT + ffmpeg) |

---

## PRODUCT OVERVIEW

**Description:** Vireel turns any YouTube/video link into three AI-generated videos — a 30-sec hook-first trailer (styled by category), a 1-min narrative trailer in a different tone, and a 3-min professional summary with B-roll overlays matched to the on-screen subject.

**Value Proposition:** Content creators and marketers get instant, ready-to-post trailers and summaries from long-form video, without manual editing.

**MVP Scope:**
- [ ] User registration and login (email/password)
- [ ] Submit a video link
- [ ] Full pipeline runs end-to-end producing all 3 outputs, each with one fixed default style (no user style picker yet)
- [ ] View live job/pipeline status per project
- [ ] Preview and download each completed output
- [ ] Retry a failed pipeline run

**Explicitly out of scope for MVP:** style picker, Dodo Payments credit-gating, email notifications, file-upload input, analytics dashboard, admin panel.

---

## TECH STACK

| Layer | Technology | Skill Reference |
|-------|------------|-----------------|
| Backend | FastAPI + Python 3.11+ | skills/BACKEND.md |
| Frontend | React + TypeScript + Vite | skills/FRONTEND.md |
| Database | PostgreSQL + SQLAlchemy | skills/DATABASE.md |
| Auth | JWT + bcrypt (email/password only, no OAuth) | skills/BACKEND.md |
| UI | Tailwind CSS + shadcn/ui | skills/FRONTEND.md |
| Testing | pytest + RTL | skills/TESTING.md |
| Deployment | Docker + GitHub Actions | skills/DEPLOYMENT.md |
| Media Pipeline | yt-dlp, OpenAI Whisper API, OpenAI GPT, ffmpeg | (new, see below) |

---

## DATABASE MODELS

### User
- id, email, hashed_password, full_name, is_active, is_verified, created_at

### RefreshToken
- id, user_id (FK → User), token, expires_at, revoked

### Project
- id, user_id (FK → User), title, source_url
- status: enum [pending, downloading, transcribing, analyzing, scripting, rendering, completed, failed]
- error_message (nullable)
- created_at, updated_at

### Transcript
- id, project_id (FK → Project, one-to-one)
- full_text
- segments (JSON: `[{start, end, text}]`)
- created_at

### Output
- id, project_id (FK → Project, many-to-one)
- output_type: enum [trailer_30s, trailer_1min, summary_3min]
- category: enum [Cinematic, Energetic, Educational, Dramatic]
- file_path
- duration_seconds
- status: enum [pending, rendering, completed, failed]
- created_at

**Relationships:** User 1—N Project; Project 1—1 Transcript; Project 1—N Output (exactly 3 per completed project).

---

## MODULES

### Module 1: Authentication
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get tokens |
| POST | /auth/refresh | Refresh token |
| POST | /auth/logout | Revoke refresh token |
| GET | /auth/me | Current user |
| PUT | /auth/me | Update profile |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /login | LoginPage | LoginForm |
| /register | RegisterPage | RegisterForm |
| /forgot-password | ForgotPasswordPage | ForgotPasswordForm |
| /profile | ProfilePage | ProfileForm (protected) |

---

### Module 2: Video Pipeline
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/projects | Submit a link, kick off async pipeline |
| GET | /api/projects | List current user's projects |
| GET | /api/projects/{id} | Get project detail + status + outputs |
| DELETE | /api/projects/{id} | Delete a project |
| POST | /api/projects/{id}/retry | Retry a failed pipeline run |
| GET | /api/projects/{id}/outputs/{output_id}/download | Download a generated output |

**Pipeline stages** (background job, must not block the request thread):
1. Validate submitted URL (reject before it reaches any subprocess)
2. Download/extract source video — **yt-dlp**
3. Transcribe audio — **OpenAI Whisper API**
4. Analyze transcript for highlights — **OpenAI GPT**
5. Generate per-output scripts — **OpenAI GPT**
6. Render all 3 outputs — self-hosted **ffmpeg** (B-roll compositing on the 3-min summary)
7. Persist Output rows, mark Project `completed` (or `failed` with `error_message`)

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /projects | ProjectListPage | ProjectCard, StatusBadge |
| /projects/new | NewProjectPage | LinkSubmitForm |
| /projects/{id} | ProjectDetailPage | PipelineProgress, OutputPreview, DownloadButton |

---

### Module 3: Library / Dashboard
**Agents:** FRONTEND-AGENT

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /dashboard | DashboardPage | RecentProjects, QuickSubmit, StatusCounts |
| /settings | SettingsPage | AccountSettingsForm |

---

## PHASE EXECUTION PLAN

> Per CLAUDE.md Workflow rule: **deliver phase by phase, pause for user confirmation after each phase** before starting the next. `/execute-prp` must stop after each Validation Gate and wait for explicit go-ahead.

**Phase 1: Foundation (4 agents in parallel)**
- DATABASE-AGENT: User, RefreshToken, Project, Transcript, Output models + Alembic migrations + database.py
- BACKEND-AGENT: main.py, config.py, project structure, env loading
- FRONTEND-AGENT: Vite + TS setup, Tailwind + shadcn/ui install, folder structure, base layout
- DEVOPS-AGENT: Dockerfiles (backend must include ffmpeg + yt-dlp binaries), docker-compose, CI skeleton, .env.example

**Validation Gate 1:** `pip install`, `alembic upgrade head`, `npm install`, `docker-compose config`

**⏸ PAUSE — confirm with user before Phase 2**

**Phase 2: Modules (backend + frontend parallel per module)**
- Auth Module: JWT endpoints (register/login/refresh/logout/me) + Login/Register/ForgotPassword/Profile pages
- Video Pipeline Module: project CRUD endpoints + async pipeline service (`services/pipeline/`: `download.py`, `transcribe.py`, `analyze.py`, `script.py`, `render.py`) + Projects list/new/detail pages
- Library/Dashboard Module: Dashboard + Settings pages (reads from Project endpoints)

**Validation Gate 2:** `ruff check backend/`, `npm run type-check`, `npm run lint`

**⏸ PAUSE — confirm with user before Phase 3**

**Phase 3: Quality (3 agents in parallel)**
- TEST-AGENT: pytest (auth + pipeline stage mocks + endpoint tests) + RTL tests, 80%+ coverage
- REVIEW-AGENT: Security audit — extra scrutiny on URL validation and subprocess invocation (yt-dlp/ffmpeg must use argument lists, never shell strings), secrets handling, rate limiting on `/auth/*` and `/api/projects`
- RESEARCH-AGENT: Validate yt-dlp/Whisper/ffmpeg usage against current best practices

**Final Validation:** `pytest --cov --cov-fail-under=80`, `npm test`, `docker-compose up -d`, `curl localhost:8000/health`

---

## VALIDATION GATES

| Gate | Commands |
|------|----------|
| 1 | `alembic upgrade head`, `npm install`, `docker-compose config` |
| 2 | `ruff check backend/`, `npm run type-check`, `npm run lint` |
| 3 | `pytest --cov --cov-fail-under=80`, `npm test` |
| Final | `docker-compose up -d`, `curl localhost:8000/health` |

---

## ENVIRONMENT VARIABLES

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vireel
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
VITE_API_URL=http://localhost:8000
```

---

## NEXT STEP

Execute with parallel agents:
/execute-prp PRPs/vireel-prp.md
