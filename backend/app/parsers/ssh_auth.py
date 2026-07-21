import re
from datetime import datetime

from app.models.event import Severity, SourceType
from app.parsers.base import BaseParser
from app.schemas.event import NormalizedEventIn

# Example lines this parser handles (standard Linux /var/log/auth.log format):
#   Jul 20 03:14:22 web01 sshd[1923]: Failed password for root from 203.0.113.5 port 51514 ssh2
#   Jul 20 03:14:25 web01 sshd[1923]: Failed password for invalid user admin from 203.0.113.5 port 51520 ssh2
#   Jul 20 03:15:01 web01 sshd[1930]: Accepted password for deploy from 198.51.100.7 port 60112 ssh2
#   Jul 20 03:16:40 web01 sshd[1940]: pam_unix(sudo:session): session opened for user root by deploy(uid=1000)

_SYSLOG_TS = r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"

_FAILED_RE = re.compile(
    _SYSLOG_TS
    + r"\s+(?P<host>\S+)\s+sshd\[\d+\]:\s+Failed password for "
    + r"(invalid user )?(?P<user>\S+) from (?P<ip>[\da-fA-F:.]+) port (?P<port>\d+)"
)
_ACCEPTED_RE = re.compile(
    _SYSLOG_TS
    + r"\s+(?P<host>\S+)\s+sshd\[\d+\]:\s+Accepted (password|publickey) for "
    + r"(?P<user>\S+) from (?P<ip>[\da-fA-F:.]+) port (?P<port>\d+)"
)
_SUDO_RE = re.compile(
    _SYSLOG_TS
    + r"\s+(?P<host>\S+)\s+sudo:\s+(?P<user>\S+)\s*:.*COMMAND=(?P<command>.+)"
)
_INVALID_USER_RE = re.compile(r"invalid user")

_CURRENT_YEAR = datetime.utcnow().year


def _parse_syslog_ts(ts_str: str) -> datetime:
    # syslog timestamps have no year; assume current year (fine for demo/portfolio data)
    dt = datetime.strptime(f"{_CURRENT_YEAR} {ts_str}", "%Y %b %d %H:%M:%S")
    return dt


class SSHAuthParser(BaseParser):
    source_type = "ssh_auth"

    def parse_line(self, line: str) -> NormalizedEventIn | None:
        m = _FAILED_RE.search(line)
        if m:
            gd = m.groupdict()
            return NormalizedEventIn(
                timestamp=_parse_syslog_ts(gd["ts"]),
                source_ip=gd["ip"],
                destination_ip=None,
                event_type="auth_failure",
                severity=Severity.MEDIUM if _INVALID_USER_RE.search(line) else Severity.LOW,
                raw_message=line,
                source_type=SourceType.SSH_AUTH,
                user=gd["user"],
                status_code="failed",
                # Note: deliberately NOT setting `port` here. The port captured
                # in an sshd log line is the *client's ephemeral source port*,
                # not a destination port being probed -- populating it would
                # falsely trigger the port_scan rule (which counts distinct
                # destination ports) on ordinary repeated SSH activity.
            )

        m = _ACCEPTED_RE.search(line)
        if m:
            gd = m.groupdict()
            return NormalizedEventIn(
                timestamp=_parse_syslog_ts(gd["ts"]),
                source_ip=gd["ip"],
                destination_ip=None,
                event_type="auth_success",
                severity=Severity.INFO,
                raw_message=line,
                source_type=SourceType.SSH_AUTH,
                user=gd["user"],
                status_code="success",
            )

        m = _SUDO_RE.search(line)
        if m:
            gd = m.groupdict()
            return NormalizedEventIn(
                timestamp=_parse_syslog_ts(gd["ts"]),
                source_ip=None,
                destination_ip=None,
                event_type="privilege_command",
                severity=Severity.LOW,
                raw_message=line,
                source_type=SourceType.SSH_AUTH,
                user=gd["user"],
                status_code=None,
            )

        return None
