"""Session journal writing with secret sanitization checks."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List
import json

from core.models import JournalEntry
from core.secret_injector import SecretInjector, SecretLeakError


class JournalWriter:
    """Append orchestration records to session journal JSON."""

    def __init__(self, journal_path: Path, secret_injector: SecretInjector) -> None:
        """Initialize writer with journal path and secret checker."""

        self.journal_path = journal_path
        self.secret_injector = secret_injector

    def append(self, entry: JournalEntry) -> None:
        """Append one journal entry after validating no secret leak."""

        payload = asdict(entry)
        blob = json.dumps(payload)
        self.secret_injector.assert_sanitized(blob)
        existing: List[dict] = []
        if self.journal_path.exists():
            existing = json.loads(self.journal_path.read_text(encoding="utf-8"))
        existing.append(payload)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        self.journal_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
