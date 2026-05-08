"""MuleSoft MCP client abstraction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import requests


@dataclass
class MuleSoftMCPClient:
    """Manage connection lifecycle and API spec retrieval for MuleSoft."""

    base_url: str
    username: str
    password: str
    _connected: bool = False

    async def connect(self) -> None:
        """Open MCP session context."""

        self._connected = True

    async def fetch_spec(self) -> Dict[str, Any]:
        """Retrieve API specification fragments from MuleSoft endpoint."""

        if not self._connected:
            raise RuntimeError("MCP client not connected")
        resp = requests.get(self.base_url, auth=(self.username, self.password), timeout=20)
        resp.raise_for_status()
        return {"source": "mulesoft", "endpoints": resp.json() if resp.headers.get('content-type','').startswith('application/json') else []}

    async def disconnect(self) -> None:
        """Close MCP session."""

        self._connected = False
