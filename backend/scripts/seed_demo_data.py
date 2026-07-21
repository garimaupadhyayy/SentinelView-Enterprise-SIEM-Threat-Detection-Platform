"""
Generates realistic sample log data (SSH auth, web access, firewall) plus
simulated attacks (brute force, port scan, SQLi) and pushes it all through
the real ingestion + correlation pipeline, so the dashboard has data to
demo immediately without needing a live log source.

Usage (inside the backend container or venv):
    python -m scripts.seed_demo_data
"""
import random
from datetime import datetime, timedelta, timezone

from app.core.db import Base, SessionLocal, engine
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.parsers.ssh_auth import SSHAuthParser
from app.parsers.web_access import WebAccessParser
from app.parsers.firewall import FirewallParser
from app.services.ingestion_service import IngestionService
from app.services.rule_seeder import seed_builtin_rules

NORMAL_USERS = ["deploy", "jsmith", "agupta", "mchen", "svc-backup"]
NORMAL_IPS = [
    "198.51.100.7", "198.51.100.23", "198.51.100.41",
    "203.0.113.201", "203.0.113.14",
]
ATTACKER_BRUTE_FORCE_IP = "45.145.6.12"
ATTACKER_PORT_SCAN_IP = "89.248.163.9"
ATTACKER_WEB_IP = "185.220.101.7"

WEB_PATHS_NORMAL = ["/", "/login", "/dashboard", "/api/health", "/static/app.js", "/about"]
SQLI_PAYLOADS = [
    "/login.php?user=admin' OR '1'='1",
    "/products?id=1 UNION SELECT username,password FROM users--",
    "/search?q=%27%20OR%201=1--",
]
XSS_PAYLOADS = [
    "/comment?text=<script>alert(1)</script>",
    "/profile?name=<img src=x onerror=alert(1)>",
]

FIREWALL_COMMON_PORTS = [22, 80, 443, 3306, 8080]


def _fmt_syslog(dt: datetime) -> str:
    return dt.strftime("%b %e %H:%M:%S").replace("  ", " ")


def _fmt_apache(dt: datetime) -> str:
    return dt.strftime("%d/%b/%Y:%H:%M:%S +0000")


def generate_ssh_lines(now: datetime) -> list[str]:
    lines = []

    # normal successful logins scattered over the last 6 hours
    for _ in range(40):
        t = now - timedelta(minutes=random.randint(1, 360))
        ip = random.choice(NORMAL_IPS)
        user = random.choice(NORMAL_USERS)
        port = random.randint(40000, 60000)
        lines.append(f"{_fmt_syslog(t)} web01 sshd[{random.randint(1000,9999)}]: Accepted password for {user} from {ip} port {port} ssh2")

    # occasional single failed login (normal typo, not an attack)
    for _ in range(8):
        t = now - timedelta(minutes=random.randint(1, 360))
        ip = random.choice(NORMAL_IPS)
        user = random.choice(NORMAL_USERS)
        port = random.randint(40000, 60000)
        lines.append(f"{_fmt_syslog(t)} web01 sshd[{random.randint(1000,9999)}]: Failed password for {user} from {ip} port {port} ssh2")

    # simulated attack: brute force -- 15 rapid failed logins from one IP
    attack_start = now - timedelta(minutes=5)
    for i in range(15):
        t = attack_start + timedelta(seconds=i * 4)
        user = random.choice(["root", "admin", "administrator", "test"])
        port = random.randint(40000, 60000)
        lines.append(f"{_fmt_syslog(t)} web01 sshd[{random.randint(1000,9999)}]: Failed password for invalid user {user} from {ATTACKER_BRUTE_FORCE_IP} port {port} ssh2")

    # simulated privilege escalation spike for a normally low-privilege user
    priv_start = now - timedelta(minutes=3)
    for i in range(6):
        t = priv_start + timedelta(seconds=i * 20)
        lines.append(f"{_fmt_syslog(t)} web01 sudo: jsmith : TTY=pts/0 ; PWD=/home/jsmith ; USER=root ; COMMAND=/bin/bash")

    return lines


def generate_web_lines(now: datetime) -> list[str]:
    lines = []
    for _ in range(60):
        t = now - timedelta(minutes=random.randint(1, 360))
        ip = random.choice(NORMAL_IPS)
        path = random.choice(WEB_PATHS_NORMAL)
        lines.append(f'{ip} - - [{_fmt_apache(t)}] "GET {path} HTTP/1.1" 200 1543')

    # simulated attack: SQLi + XSS probing from one IP
    attack_start = now - timedelta(minutes=8)
    for i, payload in enumerate(SQLI_PAYLOADS + XSS_PAYLOADS):
        t = attack_start + timedelta(seconds=i * 15)
        lines.append(f'{ATTACKER_WEB_IP} - - [{_fmt_apache(t)}] "GET {payload} HTTP/1.1" 200 512')

    return lines


def generate_firewall_lines(now: datetime) -> list[str]:
    lines = []
    for _ in range(50):
        t = now - timedelta(minutes=random.randint(1, 360))
        ip = random.choice(NORMAL_IPS)
        port = random.choice(FIREWALL_COMMON_PORTS)
        sport = random.randint(30000, 60000)
        lines.append(
            f"{_fmt_syslog(t)} fw01 kernel: IN=eth0 OUT= SRC={ip} DST=10.0.0.4 LEN=60 TOS=0x00 "
            f"PREC=0x00 TTL=64 ID={random.randint(1000,9999)} PROTO=TCP SPT={sport} DPT={port} WINDOW=29200 SYN"
        )

    # simulated attack: port scan -- 20 distinct ports hit in under a minute
    scan_start = now - timedelta(minutes=2)
    for i, port in enumerate(range(20, 40)):
        t = scan_start + timedelta(seconds=i * 2)
        sport = random.randint(30000, 60000)
        lines.append(
            f"{_fmt_syslog(t)} fw01 kernel: IN=eth0 OUT= SRC={ATTACKER_PORT_SCAN_IP} DST=10.0.0.4 LEN=60 TOS=0x00 "
            f"PREC=0x00 TTL=64 ID={random.randint(1000,9999)} PROTO=TCP SPT={sport} DPT={port} WINDOW=1024 SYN DROP"
        )

    return lines


def seed_demo_admin_user(db) -> None:
    if db.query(User).filter(User.username == "admin").first():
        return
    admin = User(
        username="admin",
        email="admin@sentinelview.local",
        hashed_password=hash_password("ChangeMe123!"),
        role=UserRole.ADMIN,
    )
    analyst = User(
        username="analyst",
        email="analyst@sentinelview.local",
        hashed_password=hash_password("ChangeMe123!"),
        role=UserRole.ANALYST,
    )
    viewer = User(
        username="viewer",
        email="viewer@sentinelview.local",
        hashed_password=hash_password("ChangeMe123!"),
        role=UserRole.VIEWER,
    )
    db.add_all([admin, analyst, viewer])
    db.commit()
    print("Seeded demo users: admin/analyst/viewer (password: ChangeMe123!) -- CHANGE THESE BEFORE ANY REAL DEPLOYMENT")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    seed_builtin_rules(db)
    seed_demo_admin_user(db)

    now = datetime.now(timezone.utc)

    ssh_events = SSHAuthParser().parse_lines(generate_ssh_lines(now))
    web_events = WebAccessParser().parse_lines(generate_web_lines(now))
    fw_events = FirewallParser().parse_lines(generate_firewall_lines(now))

    print(f"Generated {len(ssh_events)} SSH events, {len(web_events)} web events, {len(fw_events)} firewall events")

    service = IngestionService(db)
    service.ingest_events(ssh_events, source_name="seed-ssh")
    service.ingest_events(web_events, source_name="seed-web")
    service.ingest_events(fw_events, source_name="seed-firewall")

    from app.models.alert import Alert
    from app.models.event import Event

    print(f"Total events in DB: {db.query(Event).count()}")
    print(f"Total alerts in DB: {db.query(Alert).count()}")
    for a in db.query(Alert).all():
        print(f"  - [{a.severity.value.upper()}] {a.title} ({a.mitre_technique_id})")

    db.close()
    print("\nSeed complete. Start the dashboard and log in with admin / ChangeMe123!")


if __name__ == "__main__":
    main()
