"""Placeholder substitution and secret leak protection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


class SecretLeakError(RuntimeError):
    """Raised when a secret leak is detected."""


@dataclass
class SecretInjector:
    """Inject placeholders in generated curl commands with secret values."""

    mapping: Dict[str, str]

    def inject(self, command: str) -> str:
        """Replace placeholders such as <TOKEN> with secret values."""

        injected = command
        for placeholder, value in self.mapping.items():
            injected = injected.replace(placeholder, value)
        return injected

    def assert_sanitized(self, text: str) -> None:
        """Validate text does not contain raw secret values."""

        for value in self.mapping.values():
            if value and value in text:
                raise SecretLeakError("Potential secret leak detected")

    def assert_collection_sanitized(self, texts: Iterable[str]) -> None:
        """Validate iterable content has no secrets."""

        for text in texts:
            self.assert_sanitized(text)
