import re
from datetime import datetime

from app.models.event import Severity, SourceType
from app.parsers.base import BaseParser
from app.schemas.event import NormalizedEventIn

# Standard Linux iptables LOG format, e.g.:
#   Jul 20 03:14:22 fw01 kernel: IN=eth0 OUT= MAC=... SRC=203.0.113.5 DST=10.0.0.4
#     LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=1234 PROTO=TCP SPT=51514 DPT=22 WINDOW=29200 SYN

_SYSLOG_TS = r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"

_IPTABLES_RE = re.compile(
    _SYSLOG_TS
    + r"\s+(?P<host>\S+)\s+kernel:.*?SRC=(?P<src>[\da-fA-F:.]+)\s+DST=(?P<dst>[\da-fA-F:.]+)"
    + r".*?PROTO=(?P<proto>\w+).*?SPT=(?P<sport>\d+)\s+DPT=(?P<dport>\d+)"
    + r"(?P<flags>.*)"
)

_CURRENT_YEAR = datetime.utcnow().year


def _parse_syslog_ts(ts_str: str) -> datetime:
    return datetime.strptime(f"{_CURRENT_YEAR} {ts_str}", "%Y %b %d %H:%M:%S")


class FirewallParser(BaseParser):
    source_type = "firewall"

    def parse_line(self, line: str) -> NormalizedEventIn | None:
        m = _IPTABLES_RE.search(line)
        if not m:
            return None
        gd = m.groupdict()

        blocked = "DROP" in line.upper() or "DENY" in line.upper() or "REJECT" in line.upper()
        event_type = "firewall_block" if blocked else "firewall_allow"
        severity = Severity.LOW if blocked else Severity.INFO

        return NormalizedEventIn(
            timestamp=_parse_syslog_ts(gd["ts"]),
            source_ip=gd["src"],
            destination_ip=gd["dst"],
            event_type=event_type,
            severity=severity,
            raw_message=line,
            source_type=SourceType.FIREWALL,
            user=None,
            status_code="blocked" if blocked else "allowed",
            port=int(gd["dport"]),
        )
