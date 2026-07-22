# SentinelView

A self-hosted security dashboard that reads log files, spots suspicious
patterns (like login attacks or port scans), and shows everything on a
live dashboard.

<img width="1917" height="913" alt="image" src="https://github.com/user-attachments/assets/f377d34d-0f2b-496a-bfe0-84c973e63032" />


## What this actually does

1. You feed it log files (or it reads them live from a server)
2. It cleans up the messy log text into organized data
3. It checks that data against a set of rules ("5 failed logins from the
   same IP in 5 minutes = alert")
4. It shows you the results — charts, a map, and a list of alerts you can
   investigate

---

## Project structure (kept simple)

```
sentinelview/
├── backend/              The "brain" — Python program that reads logs,
│                         detects attacks, and stores everything
│
├── frontend/             The website you see in your browser
│
├── log-shipper-agent/    A small optional script for pulling logs from
│                         a real server (not needed for local testing)
│
└── docker-compose.yml    One file that starts everything with one command
```

That's genuinely it at a glance. Inside `backend/` and `frontend/` things
are split into smaller folders (parsers, pages, components, etc.) but you
don't need to touch those to just *run* the project.

---

## How to access it (local setup)

### Requirements
- **Docker Desktop** installed and running (download from docker.com)
- **VS Code** (or just a terminal — VS Code isn't required, just convenient)

### First time only

```bash
cd sentinelview
docker compose up --build -d
docker compose --profile demo run --rm seed
```

What these do:
- `docker compose up --build -d` — builds and starts the database,
  cache, backend, and frontend, all together
- `docker compose --profile demo run --rm seed` — fills the empty
  database with realistic sample logs and a few fake attacks, so the
  dashboard isn't empty

### Then open it



Log in:
| Username | Password | Can do |
|---|---|---|
| `admin` | `ChangeMe123!` | Everything |
| `analyst` | `ChangeMe123!` | View + manage alerts |
| `viewer` | `ChangeMe123!` | View only |

### Every time after that

You don't need to repeat the setup. Just:

```bash
docker compose up -d
```

Then open **http://localhost:8080** again — your data from before is
still there.

### When you're done

```bash
docker compose down
```

This turns everything off but keeps your data safe for next time.

---

## Testing it yourself

Want to see an alert get created live? Upload a log file from the
**Overview** page ("Ingest Log File" box). A ready-made fake attack log
is available on request — or make your own following the format shown
under each source type.

---

## Quick command reference

| I want to... | Run this |
|---|---|
| Start everything (first time) | `docker compose up --build -d` |
| Start everything (normal use) | `docker compose up -d` |
| Load demo data | `docker compose --profile demo run --rm seed` |
| Check what's running | `docker compose ps` |
| Stop everything | `docker compose down` |
| See live backend activity | `docker compose logs -f backend` |

---

## Want more detail?

See `GETTING_STARTED_SIMPLE.md` in this same folder for a longer,
plain-language walkthrough of every folder, every term (Docker, MySQL,
Redis, API, JWT...), and how the detection engine actually works.
