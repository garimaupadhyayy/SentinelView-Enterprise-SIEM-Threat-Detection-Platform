# SentinelView

**Enterprise Security Information and Event Management (SIEM)**

A self-hosted log aggregation and threat correlation platform. SentinelView
ingests security logs (SSH auth, web access, firewall), normalizes them into
a unified schema, evaluates them against a rule-based correlation engine
mapped to MITRE ATT&CK, and surfaces the results on a live analyst dashboard.

<img width="1916" height="902" alt="image" src="https://github.com/user-attachments/assets/207fc315-98a1-4b93-8af9-3a6415a88aa3" />


## Live Deployment

| Component | URL |
|---|---|
| **Dashboard** | `https://sentinelview-console.vercel.app/` |
| **API Docs (Swagger UI)** | `https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs` |


## Accessing the Platform

### For the project owner (Admin)

The Admin account is created automatically — **the first person to ever
register on a fresh deployment becomes Admin.** All subsequent registrations
default to Viewer.

### For anyone else you want to give access (Viewer / Analyst)

There is no self-serve "sign up" button on the login page by design (SIEM
tools are internal security software, not public products). To grant
someone access:

1. Go to the API docs: `<backend-url>/docs`
2. Expand **POST `/api/v1/auth/register`**
3. Click **"Try it out"**
4. Fill in the request body:
   ```json
   {
     "username": "their_username",
     "email": "their_email@example.com",
     "password": "a_strong_password",
     "role": "viewer"
   }
   ```
5. Click **Execute** — a `201` response confirms the account was created
6. Share the username and password with them directly (outside this system)

They can then log in at the frontend URL's `/login` page.

**Role reference:**

| Role | Can view dashboard, alerts, logs | Can change alert status | Can manage detection rules | Can manage users |
|---|---|---|---|---|
| Viewer | Yes | No | No | No |
| Analyst | Yes | Yes | No | No |
| Admin | Yes | Yes | Yes | Yes |

Only an **Admin** can promote a Viewer/Analyst to a different role — this is
done via the `PATCH /api/v1/auth/users/{id}` endpoint in the same API docs
page (Admin's own login token required, obtained by logging in through
`/auth/login` in the same docs page first).

> Roles are enforced on the backend, not just hidden in the UI — a Viewer
> account cannot perform Analyst/Admin actions even by calling the API
> directly.

---

## What It Does

1. **Ingests** logs via file upload or a REST push endpoint, using
   dedicated parsers for SSH auth logs, web server access logs, and
   firewall/iptables logs — each normalized into one unified event schema.
2. **Correlates** every incoming event against a set of configurable,
   database-stored detection rules (brute-force login, port scanning,
   impossible travel, privilege escalation, web attack signatures).
3. **Alerts**, with each one mapped to a real MITRE ATT&CK technique ID,
   scored by severity, and deduplicated via Redis so a single ongoing
   attack doesn't flood the queue with duplicate alerts.
4. **Displays** everything on a live dashboard: event volume over time,
   geo-distribution of source IPs, MITRE ATT&CK coverage heatmap, and a
   real-time event tail over WebSocket.
5. **Reports**, exporting any alert or time range as a CSV or formatted
   PDF incident report.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** React, TypeScript, Tailwind CSS, Recharts
- **Database:** MySQL (hosted on Aiven)
- **Cache / dedup:** Redis
- **Auth:** JWT with role-based access control (RBAC)
- **Deployment:** Render (backend + Redis), Vercel (frontend), Aiven (MySQL)
- **Containerization:** Docker + Docker Compose (for local development)
  
## Project Structure

```
sentinelview/
├── backend/                 FastAPI application
│   └── app/
│       ├── api/             Route handlers (auth, events, alerts, rules, ...)
│       ├── core/            Config, DB session, security/JWT, RBAC
│       ├── models/          SQLAlchemy models
│       ├── parsers/         SSH / web access / firewall log parsers
│       ├── services/        Correlation engine, alert service, ingestion
│       └── ws/               WebSocket connection manager
│
├── frontend/                 React + TypeScript dashboard
│   └── src/
│       ├── pages/            One file per screen
│       ├── components/       Reusable UI pieces
│       └── api/               Backend API client
│
├── log-shipper-agent/         Lightweight agent for streaming real server logs
├── docker-compose.yml         One-command local deployment
└── docs/                       Additional documentation
```

## Running Locally

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone <this-repo>
cd sentinelview
docker compose up --build -d
docker compose --profile demo run --rm seed   # loads demo data
```

Open **http://localhost:8080**. Demo accounts created by the seed script
(password `ChangeMe123!` for all — change before any real deployment):

| Username | Role |
|---|---|
| `admin` | Admin |
| `analyst` | Analyst |
| `viewer` | Viewer |

Full step-by-step explanation (written for beginners, no assumed
knowledge) is in `GETTING_STARTED_SIMPLE.md`.

## How Detection Works

Every alert traces back to a specific rule stored in the database — there
is no ML, no black box. Each rule defines a `rule_type` (which detection
logic runs), a time window, and a threshold. New rule instances are
created via the **Detection Rules** page in the dashboard (Admin only) —
no code change required.

| Rule | MITRE ATT&CK | Detects |
|---|---|---|
| Brute Force Login Detection | T1110 | N failed logins from one IP in a rolling window |
| Port Scan Detection | T1046 | One IP touching many distinct ports quickly |
| Impossible Travel | T1078 | Same user logging in from two geo-distant IPs too fast |
| Privilege Escalation Pattern | T1548 | Spike in sudo/su usage from one account |
| Web Attack Signature | T1190 | SQL injection / XSS patterns in request paths |

