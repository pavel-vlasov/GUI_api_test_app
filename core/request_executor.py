"""Curl command execution with response compression and persistence."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import json
import logging
import subprocess
import time
from typing import Dict, List

from core.models import IterationRecord, RequestResult

logger = logging.getLogger(__name__)
MAX_BODY_BYTES = 1024 * 1024


class RequestExecutor:
    """Execute curl commands and persist iteration results."""

    def __init__(self, output_file: Path) -> None:
        """Initialize executor with iteration result path."""

        self.output_file = output_file

    def execute_batch(self, iteration: int, commands: List[str]) -> IterationRecord:
        """Execute a batch of curl commands for one iteration."""

        started = datetime.utcnow().isoformat()
        results: List[RequestResult] = []
        for idx, command in enumerate(commands, start=1):
            results.append(self._execute_one(f"it{iteration}-{idx}", command))
        record = IterationRecord(
            iteration=iteration,
            started_at=started,
            completed_at=datetime.utcnow().isoformat(),
            results=results,
        )
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        return record

    def _execute_one(self, req_id: str, command: str) -> RequestResult:
        """Execute one curl command and parse output metadata."""

        started = time.perf_counter()
        full_cmd = f'{command} -i --silent --show-error'
        try:
            proc = subprocess.run(full_cmd, shell=True, check=False, capture_output=True, text=True)
            raw = proc.stdout or ""
            error = (proc.stderr or "").strip()
            status_line = next((ln for ln in raw.splitlines() if ln.startswith("HTTP/")), "HTTP/1.1 0")
            parts = status_line.split()
            code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            headers, body = self._split_headers_body(raw)
            body_bytes = body.encode("utf-8", errors="ignore")
            truncated = len(body_bytes) > MAX_BODY_BYTES
            if truncated:
                body = body_bytes[:MAX_BODY_BYTES].decode("utf-8", errors="ignore")
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return RequestResult(req_id, command, code, headers, body, truncated, error, elapsed_ms)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Request execution failed")
            return RequestResult(req_id, command, 0, {}, "", False, str(exc), int((time.perf_counter() - started) * 1000))

    @staticmethod
    def _split_headers_body(raw: str) -> tuple[Dict[str, str], str]:
        """Split raw curl response into headers and body."""

        sections = raw.split("\r\n\r\n") if "\r\n\r\n" in raw else raw.split("\n\n")
        header_block = sections[0] if sections else ""
        body = "\n\n".join(sections[1:]) if len(sections) > 1 else ""
        headers: Dict[str, str] = {}
        for line in header_block.splitlines()[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
        return headers, body
