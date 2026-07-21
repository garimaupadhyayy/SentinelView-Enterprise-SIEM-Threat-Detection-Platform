from abc import ABC, abstractmethod
from typing import Iterable

from app.schemas.event import NormalizedEventIn


class BaseParser(ABC):
    """
    Every concrete parser turns raw log lines of a specific format into a
    stream of NormalizedEventIn objects matching the unified schema:
    {timestamp, source_ip, destination_ip, event_type, severity,
     raw_message, source_type, user, status_code}
    Lines that don't match the expected format are skipped, not raised,
    so one malformed line doesn't kill an entire file upload.
    """

    source_type: str

    @abstractmethod
    def parse_line(self, line: str) -> NormalizedEventIn | None:
        ...

    def parse_lines(self, lines: Iterable[str]) -> list[NormalizedEventIn]:
        events = []
        for line in lines:
            line = line.rstrip("\n").strip()
            if not line:
                continue
            try:
                event = self.parse_line(line)
            except Exception:
                event = None
            if event is not None:
                events.append(event)
        return events
