# Buildlog

A small Flask app for tracking projects broken into tasks, with a progress
bar per project. Python backend, server-rendered pages, SQLite by default.

This is the Python rebuild of a JS/claude.ai-Artifact prototype of the same
idea — same concept, now a real deployable app instead of a browser-only demo.

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://localhost:8000. With no `APP_PASSWORD` set, the login gate is
skipped entirely (fine for local dev, not for a public deploy — see below).

Run the tests:

```bash
pip install pytest
pytest
```

## Deploy it (Render, free tier)

1. Push this repo to GitHub (already done if you're reading this from the repo).
2. On [Render](https://render.com), **New > Blueprint**, point it at this repo.
   It reads `render.yaml` and creates the web service automatically.
3. Render will prompt you for `APP_PASSWORD` (the one env var marked
   `sync: false`) — set it to whatever password you want to gate the app
   with. **Set this** — without it, anyone who finds the URL can open your
   tracker with no login at all.
4. Deploy. Render gives you a URL like `https://buildlog-xxxx.onrender.com` —
   open that on your phone.

### Storage caveat on the free tier

Render's free plan has no persistent disk, so the SQLite file
(`buildlog.db`) resets every time the service redeploys or spins down from
inactivity. Fine for kicking the tires; not fine for real data. Once this
is more than a pilot, either:

- Upgrade to a Render paid plan and add a persistent disk (mount it at
  `/app` or point `DATABASE_URL` at a file on it), or
- Point `DATABASE_URL` at a real Postgres instance (Render's free Postgres,
  or any other host) — the app already reads `DATABASE_URL` from the
  environment, so no code change is needed, just:
  `DATABASE_URL=postgresql://user:pass@host/dbname` (install
  `psycopg2-binary` if you go this route).

## Other hosts

Any host that runs a Docker container (Fly.io, Railway, a plain VPS) works
the same way: build the `Dockerfile`, set `APP_PASSWORD` and `SECRET_KEY`
as environment variables, and give it persistent storage for
`buildlog.db` (or point it at Postgres).

## Project layout

```
app/
  __init__.py      app factory
  models.py        Project / Task (SQLAlchemy)
  routes.py        all routes, password-gate decorator
  templates/       server-rendered Jinja pages
  static/          styles.css
tests/
  test_routes.py   route + flow tests (pytest)
run.py             local entrypoint
Dockerfile
render.yaml        Render Blueprint config
```
