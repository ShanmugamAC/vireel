# CLAUDE.md - Vireel Project Rules

> Project-specific rules for Claude Code. This file is read automatically.

---

## Project Overview

**Project Name:** Vireel
**Description:** Turns any YouTube/video link into three AI-generated videos — a 30-sec hook-first trailer, a 1-min narrative trailer, and a 3-min professional summary with B-roll overlays.
**Tech Stack:**
- Backend: FastAPI + Python 3.11+
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL + SQLAlchemy
- Auth: JWT (Email/Password only — no OAuth for now)
- UI: Tailwind CSS + shadcn/ui

---

## Project Structure

```
vireel/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py, database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── transcript.py
│   │   │   └── output.py
│   │   ├── schemas/, routers/, auth/
│   │   ├── services/
│   │   │   └── pipeline/       # yt-dlp, whisper, gpt, ffmpeg pipeline stages
│   ├── alembic/
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/, pages/, hooks/, services/, context/, types/
├── skills/           # 5 skill files
├── agents/           # Agent definitions
└── .claude/commands/ # /generate-prp, /execute-prp
```

---

## Code Standards

### Python
```python
# Type hints required
def get_user(db: Session, user_id: int) -> User:
    pass

# Async endpoints
@router.get("/users/{id}")
async def get_user(id: int, db: Session = Depends(get_db)):
    pass
```

### TypeScript
```typescript
// Interfaces required - NO any types
interface User { id: number; email: string; }

const fetchUser = async (id: number): Promise<User> => { ... };
```

---

## Forbidden

- `print()` → use `logging`
- Plain passwords → use bcrypt
- Hardcoded secrets → use env vars
- `any` type in TypeScript
- `console.log` in production
- Inline styles → use Tailwind
- Building subprocess/shell commands via string interpolation of user input (yt-dlp/ffmpeg calls must use argument lists, never shell strings, to avoid command injection)

---

## Module-Specific Rules

### Video Pipeline Module
- Every `Project` must belong to a user (`user_id` foreign key)
- `Project.status` must be one of: `pending`, `downloading`, `transcribing`, `analyzing`, `scripting`, `rendering`, `completed`, `failed`
- `Output.output_type` must be one of: `trailer_30s`, `trailer_1min`, `summary_3min`
- `Output.category` must be one of: `Cinematic`, `Energetic`, `Educational`, `Dramatic`
- The submitted video URL must be validated before it reaches any subprocess call (yt-dlp/ffmpeg)
- Pipeline stages run asynchronously (background job) and must never block the request thread

---

## API Conventions

- All endpoints prefixed with `/api/v1/`
- Use plural nouns for resources: `/projects`
- Return appropriate HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized
  - 404: Not Found
  - 409: Conflict

---

## Authentication

### JWT Configuration
- Access token expires: 30 minutes
- Refresh token expires: 7 days
- Algorithm: HS256
- Email/Password only — no OAuth providers for now

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vireel

# Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Video Pipeline
OPENAI_API_KEY=your-openai-api-key

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up -d

# Tests
pytest backend/tests -v
cd frontend && npm test

# Linting
ruff check backend/
cd frontend && npm run lint
```

---

## Commit Message Format

```
feat([module]): add [feature]
fix([module]): fix [bug]
refactor([module]): refactor [component]
test([module]): add tests for [feature]
docs: update [documentation]
```

---

## Workflow

- **Deliver phase by phase.** Pause for user confirmation after completing each phase before starting the next. This applies to `/execute-prp` runs and any other multi-step implementation work on this project.

```
1. Edit INITIAL.md (define product)
2. /generate-prp INITIAL.md
3. /execute-prp PRPs/vireel-prp.md
```

---

## Skills Reference

| Task | Skill to Read |
|------|---------------|
| Database models | skills/DATABASE.md |
| API + Auth | skills/BACKEND.md |
| React + UI | skills/FRONTEND.md |
| Testing | skills/TESTING.md |
| Deployment | skills/DEPLOYMENT.md |

---

## Agent Coordination

For complex tasks, the ORCHESTRATOR coordinates:
- DATABASE-AGENT → Backend models
- BACKEND-AGENT → API development
- FRONTEND-AGENT → UI components
- TEST-AGENT → Testing
- REVIEW-AGENT → Code review
- DEVOPS-AGENT → Deployment

Read agent definitions in `/agents/` folder.
