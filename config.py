"""Application configuration models and loaders."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class OAuthConfig:
    """OAuth 2.0 client credentials configuration."""

    token_url: str
    client_id: str
    client_secret: str
    scopes: List[str] = field(default_factory=list)


@dataclass(slots=True)
class SourceConfig:
    """Documentation source configuration for MCP fetchers."""

    mulesoft_url: Optional[str] = None
    confluence_url: Optional[str] = None
    confluence_space: Optional[str] = None
    confluence_page_title: Optional[str] = None


@dataclass(slots=True)
class AppConfig:
    """Top-level app configuration shared by GUI and CLI."""

    auth_mode: str = "oauth"
    oauth: Optional[OAuthConfig] = None
    static_headers: Dict[str, str] = field(default_factory=dict)
    sources: SourceConfig = field(default_factory=SourceConfig)
    output_dir: Path = Path("storage")
    max_iterations: int = 3


def load_env(env_path: str | Path = ".env") -> None:
    """Load environment variables from a .env file."""

    load_dotenv(dotenv_path=env_path)


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read an environment variable with optional default."""

    return os.getenv(name, default)
