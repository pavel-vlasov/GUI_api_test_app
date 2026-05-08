"""Confluence MCP client abstraction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class ConfluenceMCPClient:
    """Manage Confluence doc retrieval with MCP lifecycle semantics."""

    base_url: str
    username: str
    api_token: str
    space_key: Optional[str] = None
    page_title: Optional[str] = None
    _connected: bool = False

    async def connect(self) -> None:
        """Open connection/session to Confluence MCP bridge."""

        self._connected = True

    async def fetch_spec(self) -> Dict[str, Any]:
        """Fetch scoped documentation from Confluence REST APIs."""

        if not self._connected:
            raise RuntimeError("MCP client not connected")
        params = {"spaceKey": self.space_key, "title": self.page_title, "expand": "body.storage"}
        resp = requests.get(f"{self.base_url.rstrip('/')}/rest/api/content", params={k:v for k,v in params.items() if v}, auth=(self.username, self.api_token), timeout=20)
        resp.raise_for_status()
        return {"source": "confluence", "pages": resp.json().get("results", [])}

    async def disconnect(self) -> None:
        """Close MCP session."""

        self._connected = False
