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

## Browser Extension

The extension lives in [extension/](extension/). Load it as an unpacked Chrome/Edge extension
while the backend is running locally, then click **Save Job** on a job advertisement page.

## Frontend Dashboard

The React dashboard lives in [frontend/](frontend/).

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Current MVP Flow

1. Capture a job ad from the extension. It is stored as `not_applied`.
2. Import a job-related email through `POST /emails/import`.
3. Run `POST /matching/run`.
4. If the match is strong, the email is marked `set`, the job becomes `applied`, and an
   application record is created.

Example email import payload:

```json
{
  "subject": "Thanks for applying to Backend Engineer at Acme",
  "sender": "careers@acme.test",
  "body": "We received your application for Backend Engineer at Acme.",
  "received_at": "2026-06-27T14:00:00Z"
}
```

German emails are supported for common application confirmations too:

```json
{
  "subject": "Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote",
  "sender": "info@academicwork.de",
  "body": "Vielen Dank für Ihre Bewerbung als Softwareentwickler Java (m/w/d) - Remote bei Academic Work Germany GmbH Hamburg. Wir haben Ihre Unterlagen erhalten und prüfen diese nun.",
  "received_at": "2026-06-27T14:00:00Z"
}
```

Matching returns:

```json
{
  "processed_count": 1,
  "matched_count": 1,
  "needs_review_count": 0,
  "unmatched_count": 0
}
```
