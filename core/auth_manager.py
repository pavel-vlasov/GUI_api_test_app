"""Authentication management for OAuth and static header modes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import logging

import requests

from config import AppConfig

logger = logging.getLogger(__name__)


class AuthError(RuntimeError):
    """Raised when authentication fails."""


@dataclass
class AuthManager:
    """Manage auth headers with automatic OAuth token refresh."""

    config: AppConfig
    _access_token: Optional[str] = None
    _expires_at: Optional[datetime] = None
    _static_headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize static headers from config if selected."""

        if self.config.auth_mode == "static":
            self._static_headers = dict(self.config.static_headers)

    def get_headers(self) -> Dict[str, str]:
        """Return authorization headers for request execution."""

        if self.config.auth_mode == "static":
            return dict(self._static_headers)

        if not self._access_token or self._needs_refresh():
            self._refresh_oauth_token()
        return {"Authorization": f"Bearer {self._access_token}"}

    def _needs_refresh(self) -> bool:
        """Determine if OAuth token should be refreshed."""

        if self._expires_at is None:
            return True
        return datetime.now(timezone.utc) >= (self._expires_at - timedelta(seconds=60))

    def _refresh_oauth_token(self) -> None:
        """Fetch OAuth token from configured token endpoint."""

        if self.config.oauth is None:
            raise AuthError("OAuth config is missing")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.config.oauth.client_id,
            "client_secret": self.config.oauth.client_secret,
        }
        if self.config.oauth.scopes:
            payload["scope"] = " ".join(self.config.oauth.scopes)

        try:
            response = requests.post(self.config.oauth.token_url, data=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.exception("OAuth token refresh failed")
            raise AuthError("OAuth token refresh failed") from exc

        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not token:
            raise AuthError("Missing access_token in OAuth response")

        self._access_token = token
        self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
