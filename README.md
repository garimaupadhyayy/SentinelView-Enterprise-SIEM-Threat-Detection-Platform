# SentinelView 🛡️

## Enterprise Security Information and Event Management (SIEM)

SentinelView is a self-hosted SIEM platform designed to centralize security monitoring, normalize heterogeneous security logs, detect threats, protect sensitive information, and support analyst-driven incident investigation. The platform ingests SSH authentication, web access, and firewall logs, converts them into a unified event schema, evaluates them through configurable MITRE ATT&CK-mapped detection rules, and presents security events through a real-time analyst dashboard.

<img width="1916" height="906" alt="image" src="https://github.com/user-attachments/assets/ccb9ac58-1d76-4930-a0d2-16b37fb8b0c8" />

## Key Highlights

- **3 security log sources** normalized into a unified event schema
- **5 MITRE ATT&CK-mapped detection rules** for threat identification
- **PII masking** using regex and Luhn validation before storage
- JWT-based **Role-Based Access Control (RBAC)**
- Redis-based alert deduplication for reduced alert noise
- Real-time security monitoring through WebSockets
- CSV and PDF incident reporting

## Live Deployment

| Component | URL |
|---|---|
| **Dashboard** | `https://sentinelview-console.vercel.app/` |
| **API Docs (Swagger UI)** | `https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs` |

## Core Features

### Centralized Security Monitoring

- Ingests SSH authentication, web access, and firewall/iptables logs.
- Normalizes different log formats into a unified event schema.
- Supports file upload and REST-based log ingestion.

### Threat Detection & Correlation

- Uses a configurable rule-based detection engine.
- Implements **5 MITRE ATT&CK-mapped detection rules**.
- Assigns severity to detected events.
- Deduplicates repeated alerts using Redis.

### Sensitive Data Protection

- Detects and masks **PII** before storage.
- Uses regex-based detection and Luhn validation for applicable identifiers.
- Reduces exposure of sensitive information within security logs.

### Access Control

- Uses JWT authentication with **Role-Based Access Control (RBAC)**.
- Supports Viewer, Analyst, and Admin roles.
- Restricts administrative operations based on user role.

### Security Dashboard & Reporting

- Real-time event and alert monitoring.
- MITRE ATT&CK coverage visualization.
- Event volume and source IP analysis.
- CSV and PDF incident reporting.

## Detection Workflow

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
 MITRE ATT&CK Mapping
          ↓
 Redis Alert Deduplication
          ↓
   Real-Time Dashboard
          ↓
 CSV / PDF Incident Reports
```

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

