# Job Applications Dashboard

Local-first dashboard for tracking job applications from captured job ads and job-related emails.

## Backend Quick Start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## First Milestone

- Capture job ads as `not_applied`
- Import job-related emails as `pending`, `rejected`, `accepted`, or `unknown`
- Match emails to captured jobs
- Create application records and timeline events

## Development Workflow

Changes should be made on development branches and merged into `main` through pull requests.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/github-workflow.md](docs/github-workflow.md).
