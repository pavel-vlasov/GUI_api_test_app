"""Shared structured models for orchestration workflow."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List


@dataclass(slots=True)
class CurlCommand:
    """Generated curl command entry with metadata."""

    id: str
    command: str
    rationale: str = ""


@dataclass(slots=True)
class RequestResult:
    """Execution result for one API request."""

    id: str
    command: str
    status_code: int
    headers: Dict[str, str]
    body: str
    truncated: bool
    error: str = ""
    elapsed_ms: int = 0


@dataclass(slots=True)
class IterationRecord:
    """Persisted iteration execution results."""

    iteration: int
    started_at: str
    completed_at: str
    results: List[RequestResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for JSON serialization."""

        return {
            "iteration": self.iteration,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "results": [asdict(item) for item in self.results],
        }


@dataclass(slots=True)
class JournalEntry:
    """Session journal entry consumed by report generator."""

    timestamp: str
    iteration: int
    claude_request: str
    claude_analysis: str
    sanitized_responses: List[Dict[str, Any]]


@dataclass(slots=True)
class ApiSpec:
    """Normalized API specification derived from source docs."""

    fetched_at: str
    sources: List[str]
    endpoints: List[Dict[str, Any]]

    @staticmethod
    def empty() -> "ApiSpec":
        """Create an empty API specification object."""

        return ApiSpec(
            fetched_at=datetime.utcnow().isoformat(),
            sources=[],
            endpoints=[],
        )
