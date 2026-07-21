import re
from datetime import datetime

from app.models.event import Severity, SourceType
from app.parsers.base import BaseParser
from app.schemas.event import NormalizedEventIn

# Combined Log Format, used by both Apache and Nginx by default:
#   203.0.113.5 - - [20/Jul/2026:03:14:22 +0000] "GET /login.php?user=admin' OR '1'='1 HTTP/1.1" 200 1543 "-" "Mozilla/5.0"

_ACCESS_RE = re.compile(
    r'(?P<ip>[\da-fA-F:.]+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/[\d.]+"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\S+)'
)

_SQLI_PATTERNS = [
    re.compile(r"(\%27)|(\')|(--)|(\%23)|(#)", re.IGNORECASE),
    re.compile(r"((\%3D)|(=))[^\n]*((\%27)|(\')|(--)|(\%3B)|(;))", re.IGNORECASE),
    re.compile(r"\b(union\s+select|select\s+.+\s+from|insert\s+into|drop\s+table|or\s+1=1|' or '1'='1)\b", re.IGNORECASE),
]
_XSS_PATTERNS = [
    re.compile(r"<script.*?>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on(error|load|click|mouseover)\s*=", re.IGNORECASE),
    re.compile(r"(\%3Cscript\%3E)", re.IGNORECASE),
]


def _detect_web_attack(path: str) -> str | None:
    for p in _SQLI_PATTERNS:
        if p.search(path):
            return "sqli_signature"
    for p in _XSS_PATTERNS:
        if p.search(path):
            return "xss_signature"
    return None


def _parse_apache_ts(ts_str: str) -> datetime:
    # 20/Jul/2026:03:14:22 +0000
    return datetime.strptime(ts_str.split(" ")[0], "%d/%b/%Y:%H:%M:%S")


class WebAccessParser(BaseParser):
    source_type = "web_access"

    def parse_line(self, line: str) -> NormalizedEventIn | None:
        m = _ACCESS_RE.search(line)
        if not m:
            return None
        gd = m.groupdict()

        attack_sig = _detect_web_attack(gd["path"])
        status = gd["status"]

        if attack_sig:
            event_type = attack_sig
            severity = Severity.HIGH
        elif status.startswith("4"):
            event_type = "http_client_error"
            severity = Severity.LOW
        elif status.startswith("5"):
            event_type = "http_server_error"
            severity = Severity.MEDIUM
        else:
            event_type = "http_request"
            severity = Severity.INFO

        return NormalizedEventIn(
            timestamp=_parse_apache_ts(gd["ts"]),
            source_ip=gd["ip"],
            destination_ip=None,
            event_type=event_type,
            severity=severity,
            raw_message=line,
            source_type=SourceType.WEB_ACCESS,
            user=None,
            status_code=status,
            url_path=gd["path"][:512],
        )
