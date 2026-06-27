# GitHub Workflow

This project should use a protected `main` branch and pull requests for all changes.

## Recommended Branch Protection For `main`

In GitHub, open:

```text
Settings -> Branches -> Add branch protection rule
```

Use this branch name pattern:

```text
main
```

Enable:

- Require a pull request before merging
- Require approvals
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require conversation resolution before merging
- Do not allow bypassing the above settings
- Restrict who can push to matching branches, if available for your plan

Required status check:

```text
backend
```

Also disable direct pushes to `main` by keeping branch protection enabled.

## Daily Workflow

Create a branch:

```powershell
git checkout main
git pull
git checkout -b dev/name-of-change
```

Push the branch:

```powershell
git push -u origin dev/name-of-change
```

Open a pull request into `main`.

Merge only after GitHub Actions passes.

## Current CI

The CI pipeline runs on every push and pull request:

```text
pip install -e ".[dev]"
ruff check .
alembic upgrade head
pytest
node --check extension/src/popup.js
```

