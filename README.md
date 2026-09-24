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

### Creating a Viewer

To create another user:

1. Open the backend Swagger documentation:

```text
https://sentinelview-enterprise-siem-threat-m3sx.onrender.com/docs
