"""
Built-in detection rules. These are seeded into the `detection_rules` table
on startup (see app/services/rule_seeder.py) so that, from the engine's
perspective, a "built-in" rule and a user-created "custom" rule are exactly
the same kind of object -- just rows in a table. Adding a new rule of an
existing rule_type never requires a code change, only a new row / config
edit via the API (or by adding a YAML file under backend/rules_config/).
"""

BUILTIN_RULES = [
    {
        "name": "Brute Force Login Detection",
        "description": (
            "Fires when the same source IP produces N failed authentication "
            "events within a rolling time window."
        ),
        "rule_type": "brute_force",
        "mitre_technique_id": "T1110",
        "mitre_technique_name": "Brute Force",
        "severity": "high",
        "weight": 3,
        "config": {
            "window_seconds": 300,
            "threshold": 5,
            "event_types": ["auth_failure"],
        },
        "is_builtin": True,
    },
    {
        "name": "Port Scan Detection",
        "description": (
            "Fires when a single source IP touches many distinct destination "
            "ports/services in a short window -- classic reconnaissance behavior."
        ),
        "rule_type": "port_scan",
        "mitre_technique_id": "T1046",
        "mitre_technique_name": "Network Service Discovery",
        "severity": "medium",
        "weight": 2,
        "config": {
            "window_seconds": 60,
            "distinct_ports_threshold": 10,
        },
        "is_builtin": True,
    },
    {
        "name": "Impossible Travel / Anomalous Login",
        "description": (
            "Fires when the same user account successfully authenticates from "
            "two geographically distant IPs in a time window too short for "
            "real travel between them (basic geo-IP + time-delta heuristic)."
        ),
        "rule_type": "impossible_travel",
        "mitre_technique_id": "T1078",
        "mitre_technique_name": "Valid Accounts",
        "severity": "high",
        "weight": 3,
        "config": {
            "window_seconds": 3600,
            "min_plausible_kmh": 900,  # faster than a commercial jet -> suspicious
        },
        "is_builtin": True,
    },
    {
        "name": "Privilege Escalation Pattern",
        "description": (
            "Fires when a normal (non-admin) user account shows a spike of "
            "sudo/su command usage relative to its baseline."
        ),
        "rule_type": "priv_escalation",
        "mitre_technique_id": "T1548",
        "mitre_technique_name": "Abuse Elevation Control Mechanism",
        "severity": "medium",
        "weight": 2,
        "config": {
            "window_seconds": 600,
            "threshold": 5,
        },
        "is_builtin": True,
    },
    {
        "name": "Web Attack Signature (SQLi/XSS)",
        "description": (
            "Fires immediately when a web access log line matches a known "
            "SQL injection or cross-site scripting pattern in the request path."
        ),
        "rule_type": "web_attack_signature",
        "mitre_technique_id": "T1190",
        "mitre_technique_name": "Exploit Public-Facing Application",
        "severity": "high",
        "weight": 3,
        "config": {
            "event_types": ["sqli_signature", "xss_signature"],
            "threshold": 1,
            "window_seconds": 60,
        },
        "is_builtin": True,
    },
]
