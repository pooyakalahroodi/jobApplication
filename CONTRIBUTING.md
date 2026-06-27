# Contributing

This project uses a pull-request workflow. Do not commit directly to `main`.

## Branches

- `main`: protected production branch. Only merged pull requests should land here.
- `dev/*`: development branches for features, refactors, fixes, and workflow changes.

Use descriptive branch names:

```text
dev/browser-extension-capture
dev/email-ingestion
dev/matching-engine
fix/email-status-inference
ci/backend-test-pipeline
```

## Local Workflow

Start from the latest `main`:

```powershell
git checkout main
git pull
git checkout -b dev/my-change
```

Before opening a pull request:

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m pytest
```

Commit with clear messages:

```text
feat: add job capture endpoint
fix: correct matching score threshold
refactor: move email queries into repository
test: cover rejected email inference
ci: run backend checks on every push
docs: document Git workflow
```

## Pull Requests

Every pull request should include:

- What changed
- How it was tested
- Any migration or setup notes
- Screenshots for UI changes, when applicable

Merge only after CI passes.

