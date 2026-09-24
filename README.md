# SentinelView 🛡️

## Enterprise Security Information and Event Management (SIEM)

SentinelView is a self-hosted SIEM platform designed to centralize security monitoring, normalize heterogeneous security logs, detect threats, protect sensitive information, and support analyst-driven incident investigation.

The platform ingests SSH authentication, web access, and firewall logs, converts them into a unified event schema, evaluates events through configurable MITRE ATT&CK-mapped detection rules, and presents security activity through a real-time analyst dashboard.

<img width="1916" height="906" alt="image" src="https://github.com/user-attachments/assets/ccb9ac58-1d76-4930-a0d2-16b37fb8b0c8" />
---

## Overview

SentinelView provides centralized visibility across multiple security log sources through a unified monitoring platform.

The system combines:

- Security log ingestion and normalization
- Rule-based threat detection
- MITRE ATT&CK mapping
- PII masking
- JWT authentication and RBAC
- Redis-based alert deduplication
- Real-time security monitoring
- Incident reporting

---

## Key Highlights

- **3 security log sources** normalized into a unified event schema
- **5 MITRE ATT&CK-mapped detection rules**
- **PII masking** using regex and Luhn validation
- JWT-based **Role-Based Access Control (RBAC)**
- Redis-based alert deduplication
- Real-time monitoring through WebSockets
- CSV and PDF incident reporting
- Database-backed configurable detection rules
- MITRE ATT&CK coverage visualization

---

## Live Deployment

| Component | URL |
|---|---|
| **Dashboard** | `https://sentinelview-console.vercel.app/` |
| **API Documentation** | `https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs` |

---

# Core Features

## 1. Centralized Security Monitoring

SentinelView brings multiple security data sources into a single monitoring platform.

### Supported Sources

- SSH authentication logs
- Web server access logs
- Firewall / iptables logs

### Ingestion Methods

- File-based log ingestion
- REST-based log ingestion
- Real-time event visibility

All supported logs are parsed and converted into a common security-event schema before detection.

---

## 2. Threat Detection & Correlation

SentinelView uses a rule-based detection engine to identify suspicious activity.

The detection engine supports:

- Database-stored detection rules
- Configurable thresholds
- Configurable time windows
- Severity-based alerts
- MITRE ATT&CK technique mapping
- Redis-based alert deduplication

The current implementation uses deterministic rule-based detection rather than ML-based or black-box classification.

---

## 3. Sensitive Data Protection

SentinelView includes a data-protection layer for security events.

The platform:

- Detects applicable PII before storage
- Uses regex-based detection
- Uses Luhn validation for applicable identifiers
- Masks sensitive information
- Reduces exposure of sensitive information in stored logs

---

## 4. Authentication & Role-Based Access Control

SentinelView uses JWT authentication with backend-enforced Role-Based Access Control.

| Role | Dashboard / Alerts / Logs | Change Alert Status | Manage Detection Rules | Manage Users |
|---|---|---|---|---|
| **Viewer** | Yes | No | No | No |
| **Analyst** | Yes | Yes | No | No |
| **Admin** | Yes | Yes | Yes | Yes |

Roles are enforced at the backend API level and are not limited to frontend visibility.

---

# Security Dashboard

The dashboard provides centralized visibility into:

- Event volume over time
- Security alerts
- Source IP distribution
- Geographic distribution
- MITRE ATT&CK coverage
- Real-time event streams
- Alert status

Real-time security events are delivered through WebSockets.

---

# Detection Rules

Every generated alert is associated with a specific detection rule stored in the database.

Each rule can define:

- Detection type
- Threshold
- Time window

## Current Detection Rules

| Detection Rule | MITRE ATT&CK | Detects |
|---|---|---|
| **Brute Force Login Detection** | T1110 | Repeated failed login attempts |
| **Port Scan Detection** | T1046 | Rapid access to multiple ports |
| **Impossible Travel** | T1078 | Abnormal login locations |
| **Privilege Escalation Pattern** | T1548 | Suspicious sudo/su activity |
| **Web Attack Signature** | T1190 | SQL injection / XSS patterns |

New rule instances can be configured through the Detection Rules interface without modifying the core detection-engine source code.

---

# Detection Workflow

```text
SSH / Web / Firewall Logs
          ↓
     Log Ingestion
          ↓
   Unified Normalization
          ↓
      PII Masking
          ↓
 Detection & Correlation
          ↓
 Severity Classification
          ↓
 MITRE ATT&CK Mapping
          ↓
 Redis Alert Deduplication
          ↓
   Real-Time Dashboard
          ↓
   CSV / PDF Reports
Detection Pipeline
Incoming Security Event
          ↓
      Parse Event
          ↓
   Normalize Schema
          ↓
      Mask PII
          ↓
 Evaluate Detection Rules
          ↓
   Threshold / Time Window
          ↓
   Generate Security Alert
          ↓
 Assign Severity + MITRE ID
          ↓
 Redis Deduplication
          ↓
   Analyst Dashboard
Alert Management

Each alert contains security context including:

Detection rule
Severity
MITRE ATT&CK technique
Event information
Alert status

Redis-based deduplication helps prevent repeated events from overwhelming the alert queue during ongoing activity.

Analysts can update alert status according to their assigned permissions.

Incident Reporting

Security events and alerts can be exported for investigation and documentation.

Supported Formats
CSV
PDF

Reports provide a persistent representation of security activity for analysis and documentation.

Architecture
                         ┌─────────────────────────┐
                         │    React + TypeScript   │
                         │     Analyst Dashboard   │
                         └────────────┬────────────┘
                                      │
                              REST + WebSocket
                                      │
                         ┌────────────▼────────────┐
                         │     FastAPI Backend     │
                         │                         │
                         │ Authentication / RBAC  │
                         │ Log Ingestion           │
                         │ Normalization           │
                         │ PII Masking             │
                         │ Detection Engine        │
                         │ Alert Management        │
                         │ Incident Reporting      │
                         └────────┬────────┬───────┘
                                  │        │
                         ┌────────▼───┐ ┌──▼────────┐
                         │   MySQL    │ │   Redis   │
                         │  Database  │ │ Dedup /   │
                         │            │ │  Caching  │
                         └────────────┘ └───────────┘
Tech Stack
Layer	Technologies
Backend= Python, FastAPI, SQLAlchemy
Frontend= React, TypeScript, Tailwind CSS, Recharts
Database= MySQL
Cache / Deduplication= Redis
Authentication= JWT
Authorization= Role-Based Access Control (RBAC)
Communication= REST API, WebSockets
Deployment= Render, Vercel, Aiven
Containerization= Docker, Docker Compose
Project Structure
sentinelview/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── Authentication
│       │   ├── Events
│       │   ├── Alerts
│       │   └── Detection Rules
│       │
│       ├── core/
│       │   └── Config, DB session, JWT and RBAC
│       │
│       ├── models/
│       │   └── SQLAlchemy models
│       │
│       ├── parsers/
│       │   └── SSH / web access / firewall parsers
│       │
│       ├── services/
│       │   └── Correlation, alert and ingestion services
│       │
│       └── ws/
│           └── WebSocket connection manager
│
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       └── api/
│
├── log-shipper-agent/
├── docker-compose.yml
└── docs/
Running Locally
Prerequisites
Docker Desktop
Git
1. Clone the Repository
git clone https://github.com/garimaupadhyayy/SentinelView-Enterprise-SIEM-Threat-Detection-Platform.git

cd SentinelView-Enterprise-SIEM-Threat-Detection-Platform
2. Start the Application
docker compose up --build -d
3. Load Demo Data
docker compose --profile demo run --rm seed

This loads the local demonstration dataset and creates the configured demo accounts.

4. Open the Dashboard
http://localhost:8080

For additional beginner-friendly setup instructions, see:

GETTING_STARTED_SIMPLE.md
Demo Accounts

The demo seed creates accounts for the available RBAC roles:
Account	Role
Admin	Admin
Analyst	Analyst
Viewer	Viewer

Configure or rotate demo credentials locally before using the application outside a demonstration environment.

User & Role Management
Admin Account

On a fresh deployment, the first person to register becomes the Admin automatically.

Subsequent registrations default to the Viewer role.

Registering a User

Open the Swagger documentation:

https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs

Use:

POST /api/v1/auth/register

Example structure:

{
  "username": "analyst_user",
  "email": "analyst@example.com",
  "password": "strong_password",
  "role": "analyst"
}

SentinelView — Turning Security Events into Actionable Insights.
~Garima Upadhyay
