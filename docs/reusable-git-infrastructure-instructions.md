# Reusable Git Infrastructure Instructions

Copy this instruction into a new project when you want the same professional Git workflow.

## Instruction For Codex

Set up this project with a professional Git and GitHub workflow.

Use these rules:

1. Never work directly on `main`.
2. Create a development branch for every change.
3. Use pull requests to merge into `main`.
4. Keep `main` protected from direct pushes.
5. Run tests, linting, and migration checks in GitHub Actions on every push and pull request.
6. Keep secrets and machine-specific values out of Git.
7. Commit a `.env.example` file, but never commit real `.env` files.
8. Use clear commit messages.
9. Keep the working tree clean after each completed change.

Create or verify this repository structure:

```text
.github/
  workflows/
    ci.yml
  pull_request_template.md

docs/
  github-workflow.md

CONTRIBUTING.md
.gitignore
README.md
```

Create `.gitignore` entries for local/private/generated files:

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.env
.env.*
!.env.example
!**/.env.example
*.db
*.sqlite
*.sqlite3
*.egg-info/
htmlcov/
.coverage
dist/
build/
node_modules/
```

Create a `.env.example` file for safe sample configuration. Do not include real tokens, passwords, API keys, OAuth secrets, database passwords, or private endpoints.

Use this branch strategy:

```text
main
  protected branch
  only receives merged pull requests

dev/*
  feature and workflow branches

fix/*
  bug-fix branches

ci/*
  pipeline and automation branches

docs/*
  documentation branches
```

Use commit messages like:

```text
feat: add job capture endpoint
fix: correct matching score threshold
refactor: move queries into repository layer
test: cover email status inference
ci: run backend checks on every push
docs: document git workflow
```

Create `.github/workflows/ci.yml` so CI runs on every push and pull request. For a Python/FastAPI backend, use:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install backend
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Lint
        run: ruff check .
      - name: Run migrations
        run: alembic upgrade head
      - name: Test
        run: pytest
```

Create `.github/pull_request_template.md`:

```markdown
## Summary

- 

## Testing

- [ ] `ruff check .`
- [ ] `alembic upgrade head`
- [ ] `pytest`

## Notes

- 
```

Create `CONTRIBUTING.md` explaining:

- no direct commits to `main`
- branch naming rules
- local test commands
- pull request requirements
- merge only after CI passes

Create `docs/github-workflow.md` explaining how to protect `main` in GitHub:

```text
Settings -> Branches -> Add branch protection rule -> main
```

Enable:

```text
Require a pull request before merging
Require approvals
Require status checks to pass before merging
Require branches to be up to date before merging
Require conversation resolution before merging
Do not allow bypassing the above settings
```

Required status check:

```text
backend
```

Local development flow:

```powershell
git checkout main
git pull
git checkout -b dev/name-of-change
```

Before committing:

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m pytest
```

Push the branch:

```powershell
git push -u origin dev/name-of-change
```

Open a pull request into `main`.

After the pull request is approved and CI is green, merge it into `main`.

If GitHub tooling can create pull requests, create the PR automatically. If not, push the branch and provide the pull request creation URL.

## Notes For This Project

This project uses the same model:

- `main` is the protected branch.
- work happens on `dev/*` branches.
- GitHub Actions runs backend checks.
- private values live in `.env`.
- safe sample values live in `backend/.env.example`.

