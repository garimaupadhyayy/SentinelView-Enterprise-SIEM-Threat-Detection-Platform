#!/usr/bin/env python3
"""
SentinelView Log Shipper Agent
-------------------------------
A tiny, dependency-light agent that tails a local log file (like `tail -f`)
and forwards new lines to a SentinelView ingestion API in batches. Meant to
run alongside the service producing logs (e.g. on the box running sshd,
nginx, or iptables logging) with zero external dependencies beyond
`requests`.

Usage:
    python3 shipper.py --file /var/log/auth.log --source-type ssh_auth \
        --api-url http://sentinelview:8000/api/v1/events/push \
        --api-key change-me-shared-secret

Run multiple instances (one per log file/source type) via systemd units,
or via the provided docker-compose service for the seeded demo.
"""
import argparse
import logging
import sys
import time

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [shipper] %(levelname)s %(message)s"
)
logger = logging.getLogger("sentinelview-shipper")


class LogShipper:
    def __init__(
        self,
        file_path: str,
        source_type: str,
        api_url: str,
        api_key: str,
        source_name: str,
        batch_size: int = 50,
        batch_interval_seconds: float = 2.0,
        from_beginning: bool = False,
    ):
        self.file_path = file_path
        self.source_type = source_type
        self.api_url = api_url
        self.api_key = api_key
        self.source_name = source_name
        self.batch_size = batch_size
        self.batch_interval_seconds = batch_interval_seconds
        self.from_beginning = from_beginning
        self._buffer: list[str] = []
        self._last_flush = time.monotonic()

    def _flush(self) -> None:
        if not self._buffer:
            return
        payload = {
            "source_type": self.source_type,
            "raw_lines": self._buffer,
            "source_name": self.source_name,
        }
        try:
            resp = requests.post(
                self.api_url,
                params={"api_key": self.api_key},
                json=payload,
                timeout=10,
            )
            if resp.status_code >= 300:
                logger.warning(
                    "Ingestion API returned %s: %s", resp.status_code, resp.text[:300]
                )
            else:
                logger.info("Shipped %d lines (%s)", len(self._buffer), resp.status_code)
        except requests.RequestException as exc:
            logger.error("Failed to ship batch: %s. Lines will be dropped.", exc)
        finally:
            self._buffer = []
            self._last_flush = time.monotonic()

    def _maybe_flush(self) -> None:
        if len(self._buffer) >= self.batch_size:
            self._flush()
        elif self._buffer and (time.monotonic() - self._last_flush) >= self.batch_interval_seconds:
            self._flush()

    def run(self) -> None:
        logger.info(
            "Tailing %s as source_type=%s -> %s", self.file_path, self.source_type, self.api_url
        )
        with open(self.file_path, "r") as f:
            if not self.from_beginning:
                f.seek(0, 2)  # jump to end, like `tail -f`

            while True:
                line = f.readline()
                if line:
                    self._buffer.append(line.rstrip("\n"))
                    self._maybe_flush()
                else:
                    self._maybe_flush()
                    time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="SentinelView log shipper agent")
    parser.add_argument("--file", required=True, help="Path to the log file to tail")
    parser.add_argument(
        "--source-type", required=True, choices=["ssh_auth", "web_access", "firewall"]
    )
    parser.add_argument("--api-url", required=True, help="SentinelView ingestion push endpoint")
    parser.add_argument("--api-key", required=True, help="Shared ingestion API key")
    parser.add_argument("--source-name", default=None, help="Label shown in the dashboard")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--batch-interval", type=float, default=2.0)
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Read the whole file from the start instead of only new lines",
    )
    args = parser.parse_args()

    shipper = LogShipper(
        file_path=args.file,
        source_type=args.source_type,
        api_url=args.api_url,
        api_key=args.api_key,
        source_name=args.source_name or f"shipper-{args.source_type}",
        batch_size=args.batch_size,
        batch_interval_seconds=args.batch_interval,
        from_beginning=args.from_beginning,
    )

    try:
        shipper.run()
    except FileNotFoundError:
        logger.error("File not found: %s", args.file)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
