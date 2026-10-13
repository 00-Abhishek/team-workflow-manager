# Team Task & Workflow Manager

A collaborative project-management web app: teams create projects, break work into
tasks, assign owners, set due dates, move tasks through a controlled workflow, and
keep a discussion and activity history. Think of a small, focused project tool —
not a full Jira/Trello replacement.

## Features

- Sign-in with JWT auth.
- Create projects; the creator becomes the project **owner** and a member.
- Add members to a project and enforce membership on every request.
- Create tasks with title, description, status, priority, assignee and due date.
- **Kanban board** (To Do → In Progress → In Review → Done) and a list view.
- Filter by project, status, priority, assignee and search.
- Comments and a per-task activity timeline.
- Project summary counts and **overdue** task tracking.
- Enforced workflow: illegal status jumps are rejected with `422`.
- Assignments are validated: a task can only be assigned to a project member.

## Architecture

```
React (Vite)
  ├─ project list / project detail
  ├─ task list / Kanban board / filters
  └─ forms and comments
        │ fetch/JSON
        ▼
FastAPI
  ├─ authentication / project-membership checks
  ├─ task workflow rules / API schemas
  └─ service layer (testable business rules)
        │
        ▼
PostgreSQL (SQLAlchemy)
```

Authorization is based on **project membership and role**, not just knowing an id:
non-members receive `404` for a project so its existence is not leaked.

## Tech stack

| Layer     | Technology                                |
|-----------|-------------------------------------------|
| Frontend  | React 18, Vite, React Router, plain CSS   |
| Backend   | FastAPI, Pydantic v2, SQLAlchemy 2, PyJWT |
| Database  | PostgreSQL 16                             |
| Tests     | pytest, FastAPI TestClient                |
| Packaging | Docker, docker-compose                    |

## Prerequisites

- Node.js 20 LTS and npm
- Python 3.11+
- PostgreSQL 16 (or Docker)
- Git

```bash
node --version && npm --version && python --version && git --version
```

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

The backend creates its schema and seeds demo data on first start.

## Manual local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DATABASE_URL="postgresql+psycopg://workflow:workflow@localhost:5432/workflow"
export SECRET_KEY="dev-secret-change-me"

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # sets VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

## Demo accounts

| Email               | Password | Global role | Notes                     |
|---------------------|----------|-------------|---------------------------|
| admin@example.com   | admin123 | admin       | Can see all projects      |
| lead@example.com    | lead123  | user        | Owner of "Website Launch" |
| dev@example.com     | dev123   | user        | Member of that project    |

## Environment variables

| Variable         | Purpose                                            | Default  |
|------------------|----------------------------------------------------|----------|
| `DATABASE_URL`   | SQLAlchemy database URL                            | postgres |
| `SECRET_KEY`     | JWT signing key — set a strong value in production | dev value |
| `CORS_ORIGINS`   | Comma-separated allowed frontend origins           | http://localhost:5173 |

Only `.env.example` is committed. Never commit real secrets.

## API overview

| Method | Path                                  | Notes                              |
|--------|---------------------------------------|------------------------------------|
| POST   | `/api/auth/register`                  | Create a user                      |
| POST   | `/api/auth/token`                     | Login (OAuth2 password form)       |
| GET    | `/api/auth/me`                        | Current user                       |
| GET    | `/api/users`                          | List users (to add members)        |
| POST   | `/api/projects`                       | Create project                     |
| GET    | `/api/projects`                       | Projects you belong to             |
| GET    | `/api/projects/{id}`                  | Project + members (members only)   |
| POST   | `/api/projects/{id}/members`          | Add a member                       |
| GET    | `/api/projects/{id}/summary`          | Status counts + overdue            |
| POST   | `/api/projects/{id}/tasks`            | Create task                        |
| GET    | `/api/tasks`                          | List + filter tasks                |
| GET    | `/api/tasks/{id}`                     | Task detail with comments/events   |
| PATCH  | `/api/tasks/{id}`                     | Update status/priority/assignee/due|
| POST   | `/api/tasks/{id}/comments`            | Add comment                        |
| GET    | `/api/dashboard/summary`              | Cross-project counts               |

Example:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -d "username=lead@example.com&password=lead123" | jq -r .access_token)

curl -s http://localhost:8000/api/projects -H "Authorization: Bearer $TOKEN"
```

## Tests

```bash
cd backend
pytest -q
```

The suite covers auth, project creation, membership authorization, assignment
validation, workflow transitions, comments, summaries and overdue detection. Tests
run against an in-memory SQLite database, so no PostgreSQL is needed to run them.

## Project structure

```
team-workflow-manager/
  frontend/          React + Vite SPA
  backend/
    app/
      api/           routers + dependencies
      core/          settings + security
      db/            session, base, seed
      models/        SQLAlchemy models
      schemas/       Pydantic schemas
      services/      project + task business rules
    tests/
  docker-compose.yml
  .env.example
```

## Security notes

- Passwords are hashed with bcrypt; tokens are signed JWTs.
- Every request checks project membership and role on the backend.
- Non-members get `404` (not `403`) so project existence is not leaked.
- Input is validated server-side even though the frontend validates too.

## Known limitations & next steps

- Schema is created with SQLAlchemy `create_all` for the MVP; Alembic migrations are
  the natural next step.
- Real-time updates (WebSockets), email notifications and recurring tasks are
  intentionally out of the MVP scope.

## Attribution

Built as a learning/demonstration project with FastAPI, React, Vite and PostgreSQL.
