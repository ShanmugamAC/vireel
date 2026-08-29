# INITIAL.md - Vireel Product Definition

> Turn any video link into three AI-generated trailers/summaries.

---

## PRODUCT

### Name
Vireel

### Description
Vireel is a web app that turns any YouTube/video link into three AI-generated videos:
- **30-sec Trailer** — hook-first, styled per a chosen category (Cinematic / Energetic / Educational / Dramatic)
- **1-min Trailer** — a different category/tone, more narrative build-up
- **3-min Summary (Main Video)** — full concept condensed, professional, with B-Roll overlays matching the subject currently on screen

**Pipeline flow:** link → validate → download/extract → transcribe → analyze highlights → script → render 3 outputs → store → preview/download.

### Target User
Content creators and marketers repurposing long-form video into trailers/shorts.

### Type
- [x] SaaS (Software as a Service)

---

## TECH STACK

### Backend
- [x] FastAPI + Python 3.11+

### Frontend
- [x] React + Vite + TypeScript

### Database
- [x] PostgreSQL + SQLAlchemy

### Authentication
- [x] Email/Password only (JWT). No Google OAuth for now.

### UI Framework
- [x] Tailwind CSS + shadcn/ui

### Payments
- [ ] None for MVP — the app is fully free. Dodo Payments credit-gating is a deferred, post-MVP decision (packs vs. subscription vs. both — TBD).

---

## MODULES

### Module 1: Authentication (Required)

**Description:** User authentication and authorization.

**Models:**
- User: id, email, hashed_password, full_name, is_active, is_verified, created_at
- RefreshToken: id, user_id, token, expires_at, revoked

**API Endpoints:**
- POST /auth/register - Create new account
- POST /auth/login - Login with email/password
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Revoke refresh token
- GET /auth/me - Get current user profile
- PUT /auth/me - Update profile

**Frontend Pages:**
- /login - Login page
- /register - Registration page
- /forgot-password - Forgot password page
- /profile - User profile page (protected)

---

### Module 2: Video Pipeline

**Description:** Core product loop — submit a video link, run it through an async pipeline, and produce three downloadable outputs.

**Models:**
```
Project:
  - id, user_id (FK)
  - title
  - source_url
  - status: enum [pending, downloading, transcribing, analyzing, scripting, rendering, completed, failed]
  - error_message (nullable)
  - created_at, updated_at

Transcript:
  - id, project_id (FK)
  - full_text
  - segments (JSON: [{start, end, text}])
  - created_at

Output:
  - id, project_id (FK)
  - output_type: enum [trailer_30s, trailer_1min, summary_3min]
  - category: enum [Cinematic, Energetic, Educational, Dramatic]
  - file_path
  - duration_seconds
  - status: enum [pending, rendering, completed, failed]
  - created_at
```

**Pipeline stages** (run as an async background job, never blocking the request thread):
1. Validate submitted URL
2. Download/extract source video via **yt-dlp**
3. Transcribe audio via **OpenAI Whisper API**
4. Analyze transcript for highlights via **OpenAI GPT**
5. Generate per-output scripts via **OpenAI GPT**
6. Render all 3 outputs via a self-hosted **ffmpeg** pipeline (with B-Roll overlay compositing on the 3-min summary)
7. Persist outputs and mark project completed

**API Endpoints:**
```
POST   /api/projects                              - Submit a link, kick off pipeline
GET    /api/projects                               - List current user's projects
GET    /api/projects/{id}                          - Get project detail + status + outputs
DELETE /api/projects/{id}                           - Delete a project
POST   /api/projects/{id}/retry                     - Retry a failed pipeline run
GET    /api/projects/{id}/outputs/{output_id}/download - Download a generated output
```

**Frontend Pages:**
```
/projects           - List of projects with live status
/projects/new        - Submit a new video link
/projects/{id}       - Pipeline progress, output previews, download buttons
```

---

### Module 3: Library / Dashboard

**Description:** Landing/overview page and the browsable history of past projects (the project list from Module 2 serves as the library view).

**Frontend Pages:**
- /dashboard - Overview: recent projects, quick "submit a link" action, basic counts (in progress / completed / failed)
- /settings - User settings and preferences

---

## MVP SCOPE

### Must Have (MVP)
- [x] User registration and login (email/password)
- [x] Submit a video link
- [x] Full pipeline runs end-to-end producing all 3 outputs, each with one fixed default style (no user style picker yet)
- [x] View live job/pipeline status per project
- [x] Preview and download each completed output
- [x] Retry a failed pipeline run

### Nice to Have (Post-MVP)
- [ ] User-selectable category/tone per trailer
- [ ] Dodo Payments credit system gating renders (packs and/or subscription — model TBD)
- [ ] Email notifications on render completion/failure
- [ ] File upload as an alternative to a link
- [ ] Analytics dashboard (renders/day, processing time, success/failure rates)
- [ ] Admin panel

---

## ACCEPTANCE CRITERIA

### Authentication
- [ ] User can register with email/password
- [ ] User can login with email/password
- [ ] JWT tokens work correctly with refresh
- [ ] Protected routes redirect to login

### Video Pipeline
- [ ] Submitting a valid link creates a Project and starts the pipeline asynchronously
- [ ] Invalid/malformed URLs are rejected before reaching yt-dlp
- [ ] Project status updates as the pipeline progresses through each stage
- [ ] Pipeline produces 3 valid, playable video files (30s trailer, 1min trailer, 3min summary with B-roll)
- [ ] User can preview and download each completed output
- [ ] Failed jobs surface an error message and support retry

### Quality
- [ ] All API endpoints documented in OpenAPI
- [ ] Backend test coverage 80%+
- [ ] Frontend TypeScript strict mode passes
- [ ] Docker builds and runs successfully

---

## SPECIAL REQUIREMENTS

### Security
- [x] Rate limiting on auth endpoints and on project-submission (pipeline runs are expensive)
- [x] Input validation on all endpoints
- [x] Strict validation/sanitization of the submitted URL before it ever reaches yt-dlp/ffmpeg — always invoke subprocesses with argument lists, never string-interpolated shell commands, to prevent command injection
- [x] SQL injection prevention
- [x] XSS prevention

### Integrations
- [x] OpenAI API (Whisper for transcription, GPT for highlight analysis + script generation)
- [x] yt-dlp for video download/extraction
- [x] ffmpeg for rendering and B-roll compositing

### Architecture notes for /generate-prp
- Needs an async job runner for the pipeline (FastAPI BackgroundTasks for MVP simplicity, or Celery+Redis if concurrency/retries demand it) — pipeline runs take minutes, so requests must return immediately with a job/project id.
- Needs file storage for source videos and rendered outputs — local disk/volume is fine for MVP; note S3-compatible object storage as a post-MVP upgrade path.

---

## AGENTS

> These 6 agents will build your product in parallel:

| Agent | Role | Works On |
|-------|------|----------|
| DATABASE-AGENT | Creates all models and migrations | User, RefreshToken, Project, Transcript, Output |
| BACKEND-AGENT | Builds API endpoints and services | Auth + Video Pipeline endpoints and pipeline stage services |
| FRONTEND-AGENT | Creates UI pages and components | Login/Register/Profile, Projects list/new/detail, Dashboard |
| DEVOPS-AGENT | Sets up Docker, CI/CD, environments | Infrastructure incl. ffmpeg/yt-dlp availability in containers |
| TEST-AGENT | Writes unit and integration tests | All code |
| REVIEW-AGENT | Security and code quality audit | All code, with extra scrutiny on subprocess/URL handling |

---

# READY?

```bash
/generate-prp INITIAL.md
```

Then:

```bash
/execute-prp PRPs/vireel-prp.md
```
