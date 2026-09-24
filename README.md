# SentinelView 🛡️

## Enterprise Security Information and Event Management (SIEM)

SentinelView is a self-hosted SIEM platform designed to centralize security monitoring, normalize heterogeneous security logs, detect threats, protect sensitive information, and support analyst-driven incident investigation. The platform ingests SSH authentication, web access, and firewall logs, converts them into a unified event schema, evaluates them through configurable MITRE ATT&CK-mapped detection rules, and presents security events through a real-time analyst dashboard.

<img width="1916" height="906" alt="image" src="https://github.com/user-attachments/assets/ccb9ac58-1d76-4930-a0d2-16b37fb8b0c8" />

<div align="center">

## Overview

SentinelView is a self-hosted SIEM platform designed to centralize security monitoring, normalize heterogeneous security logs, detect suspicious activity, protect sensitive information, and support analyst-driven incident investigation.

The platform ingests SSH authentication, web access, and firewall logs, converts them into a unified event schema, evaluates events through configurable MITRE ATT&CK-mapped detection rules, and presents security activity through a real-time analyst dashboard.

<br>

## Key Highlights

- **3 security log sources** normalized into a unified event schema
- **5 MITRE ATT&CK-mapped detection rules**
- **PII masking** using regex and Luhn validation
- JWT-based **Role-Based Access Control (RBAC)**
- Redis-based alert deduplication
- Real-time security monitoring through WebSockets
- CSV and PDF incident reporting
- Configurable database-backed detection rules
- Live MITRE ATT&CK coverage visualization

<br>

## Live Deployment

| Component | URL |
|---|---|
| **Dashboard** | `https://sentinelview-console.vercel.app/` |
| **API Documentation** | `https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs` |

> The backend runs on a free-tier instance and may take 30–60 seconds to respond after a period of inactivity due to cold starts.

<br>

## Core Features

### Centralized Security Monitoring

SentinelView brings multiple security data sources into one monitoring platform.

- SSH authentication logs
- Web server access logs
- Firewall / iptables logs
- File-based log ingestion
- REST-based log ingestion
- Unified security-event schema
- Real-time event visibility

### Threat Detection & Correlation

The platform uses a rule-based detection engine to identify suspicious activity.

- Database-stored detection rules
- Configurable thresholds
- Configurable time windows
- Severity-based alerts
- MITRE ATT&CK mapping
- Redis-based alert deduplication

### Sensitive Data Protection

SentinelView includes a data-protection layer for security events.

- Detects applicable PII before storage
- Uses regex-based detection
- Uses Luhn validation for applicable identifiers
- Masks sensitive information
- Reduces exposure of sensitive information in stored logs

### Access Control

SentinelView uses JWT authentication and Role-Based Access Control.

| Role | Dashboard / Alerts / Logs | Change Alert Status | Manage Detection Rules | Manage Users |
|---|---|---|---|---|
| Viewer | Yes | No | No | No |
| Analyst | Yes | Yes | No | No |
| Admin | Yes | Yes | Yes | Yes |

<br>

## Creating Users & Roles

### Admin Account

On a **fresh deployment**, the first person to register becomes the **Admin** automatically.

All subsequent registrations default to the **Viewer** role.

### Creating a Viewer / Analyst

To create another user:

1. Open the backend Swagger documentation:

```text
https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs
Expand:
POST /api/v1/auth/register
Click Try it out.
Provide the required user details.

Example:

{
  "username": "analyst_user",
  "email": "analyst@example.com",
  "password": "strong_password",
  "role": "analyst"
}
Click Execute.

A successful response confirms that the account has been created.

The user can then log in through the frontend dashboard.

Changing User Roles

Only an Admin can promote or change another user's role.

Use:

PATCH /api/v1/auth/users/{id}

The Admin's authentication token is required.

The Admin first authenticates through:

POST /api/v1/auth/login

and uses the returned JWT token for authorized administrative operations.

Supported roles:

viewer
analyst
admin

Roles are enforced on the backend, not only through frontend visibility. A Viewer cannot perform Analyst/Admin operations by directly calling protected APIs.

<br>
Security Dashboard

The dashboard provides centralized visibility into:

Event volume over time
Security alerts
Source IP distribution
Geographic distribution
MITRE ATT&CK coverage
Real-time event streams
Alert status

Real-time events are delivered through WebSockets.

<br>
Detection Rules

Every alert traces back to a specific rule stored in the database.

Each rule defines:

Detection type
Threshold
Time window

Current detection rules include:

Detection Rule	MITRE ATT&CK	Detects
Brute Force Login Detection	T1110	Repeated failed login attempts
Port Scan Detection	T1046	Rapid access to multiple ports
Impossible Travel	T1078	Abnormal login locations
Privilege Escalation Pattern	T1548	Suspicious sudo/su activity
Web Attack Signature	T1190	SQL injection / XSS patterns

New rule instances can be configured through the Detection Rules page without changing the detection-engine source code.

<br>
Detection Workflow
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
<br>
How Detection Works

Every incoming event is processed through the rule-based detection engine.

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

There is no ML-based detection or black-box classification in the current implementation.

<br>
Alert Management

Each alert contains security context including:

Detection rule
Severity
MITRE ATT&CK technique
Event information
Alert status

Redis-based deduplication prevents repeated events from overwhelming the alert queue during ongoing activity.

Analysts can update alert status according to their assigned permissions.

<br>
Incident Reporting

Security events and alerts can be exported for investigation and documentation.

Supported formats:

CSV
PDF incident reports

These reports provide a persistent representation of security activity for analysis and documentation.

<br>
Architecture
                         ┌─────────────────────────┐
                         │    React + TypeScript    │
                         │     Analyst Dashboard    │
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
                         │ Database   │ │ Dedup /   │
                         │            │ │ Caching   │
                         └────────────┘ └───────────┘
<br>
Tech Stack
Layer	Technologies
Backend	Python, FastAPI, SQLAlchemy
Frontend	React, TypeScript, Tailwind CSS, Recharts
Database	MySQL
Cache / Deduplication	Redis
Authentication	JWT
Authorization	Role-Based Access Control (RBAC)
Communication	REST API, WebSockets
Deployment	Render, Vercel, Aiven
Containerization	Docker, Docker Compose
<br>
Project Structure
sentinelview/
├── backend/
│   └── app/
│       ├── api/
│       │   └── Route handlers
│       │       ├── Authentication
│       │       ├── Events
│       │       ├── Alerts
│       │       └── Detection Rules
│       │
│       ├── core/
│       │   └── Config, DB session, JWT and RBAC
│       │
│       ├── models/
│       │   └── SQLAlchemy models
│       │
│       ├── parsers/
│       │   └── SSH / web access / firewall log parsers
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
<br>
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

For beginner-friendly setup instructions, see:

GETTING_STARTED_SIMPLE.md
<br>
Demo Accounts

The demo seed creates accounts for the available RBAC roles:

Account	Role
Admin	Admin
Analyst	Analyst
Viewer	Viewer

Demo credentials should be configured or rotated locally. Never reuse demo credentials for production deployments.

Do not commit real passwords, API keys, JWT secrets, or other sensitive information to the repository.

<br>
Data Ingestion

SentinelView supports:

File-Based Ingestion

Security log files can be uploaded and processed through the appropriate parser.

REST-Based Ingestion

Security events can also be pushed through the ingestion API.

The supported log sources are:

SSH authentication logs
Web server access logs
Firewall / iptables logs

Each source is parsed and normalized before entering the detection pipeline.

<br>
API Reference

Complete API documentation is available through Swagger UI:

https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs

Key authentication and administration endpoints include:

Method	Endpoint	Purpose
POST	/api/v1/auth/register	Register a user
POST	/api/v1/auth/login	Authenticate and obtain JWT
PATCH	/api/v1/auth/users/{id}	Admin role management
WS	WebSocket endpoint	Real-time security-event updates

Additional APIs cover:

Security-event ingestion
Alerts
Detection rules
Security logs
Reporting
Dashboard data

Refer to Swagger for the complete API specification.

<br>
Security Configuration

Before using SentinelView outside a local demonstration environment:

JWT Secret

Change:

JWT_SECRET_KEY

to a strong, randomly generated secret.

Ingestion API Key

Configure:

INGEST_API_KEY

with a secure value.

The ingestion endpoint uses an API key for machine-to-machine communication from the log-shipper agent.

Application Credentials

Use strong passwords for all application accounts.

Environment Variables

Never commit:

.env

files containing secrets to GitHub.

Environment-specific configuration should be used for:

Database credentials
JWT secrets
Ingestion API keys
External service credentials
<br>
Security & Privacy Considerations

SentinelView demonstrates controlled handling of security data through:

PII masking before storage
JWT authentication
Backend-enforced RBAC
Role-based administrative controls
Security-event normalization
Severity-based alerting
API-key protected machine-to-machine ingestion
Centralized security monitoring
Incident-oriented reporting

The platform is intended as a cybersecurity learning and portfolio project and should undergo additional security hardening before production use.

<br>
Security Design Principles
Least-Privilege Access

Platform capabilities are separated according to user roles.

Sensitive Data Protection

Applicable PII is masked before security events are stored.

Centralized Visibility

Security events from multiple sources are normalized and presented through a single monitoring interface.

Traceable Detection

Alerts are associated with specific detection rules and MITRE ATT&CK techniques.

Controlled Ingestion

Machine-to-machine ingestion is protected using an API key.

Security Reporting

Detected activity can be exported for investigation and documentation.

<br>
Future Scope

The following are potential future extensions and are not currently represented as implemented features:

Data classification capabilities
Data Loss Prevention (DLP) integrations
Cloud security log integrations
Additional threat-intelligence sources
Machine-learning based anomaly detection
Expanded data-governance capabilities
Additional privacy controls
Multi-tenant security monitoring
Advanced sensitive-data discovery
Extended security analytics
<br>
