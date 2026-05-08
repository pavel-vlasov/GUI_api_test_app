"""CLI entry point reusing orchestration modules without GUI dependencies."""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import os

from config import AppConfig, OAuthConfig, SourceConfig, load_env
from core.journal_writer import JournalWriter
from core.orchestrator import Orchestrator
from core.report_generator import ReportGenerator
from core.request_executor import RequestExecutor
from core.secret_injector import SecretInjector
from llm.claude_cli_adapter import ClaudeCliAdapter
from mcp.confluence_mcp import ConfluenceMCPClient
from mcp.mulesoft_mcp import MuleSoftMCPClient


def main() -> None:
    """Run autonomous API test session from command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".env")
    parser.add_argument("--auth-mode", choices=["oauth", "static"], default="oauth")
    parser.add_argument("--output-dir", default="storage")
    args = parser.parse_args()

    load_env(args.config)
    oauth = OAuthConfig(
        token_url=os.getenv("TOKEN_URL", ""),
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        scopes=os.getenv("SCOPES", "").split(),
    ) if args.auth_mode == "oauth" else None

    app_config = AppConfig(auth_mode=args.auth_mode, oauth=oauth, output_dir=Path(args.output_dir), sources=SourceConfig(os.getenv("MULESOFT_URL"), os.getenv("CONFLUENCE_URL")))
    secret_map = {"<TOKEN>": os.getenv("API_TOKEN", ""), "<API_KEY>": os.getenv("API_KEY", "")}
    secret_injector = SecretInjector(secret_map)
    orchestrator = Orchestrator(
        config=app_config,
        llm_adapter=ClaudeCliAdapter(),
        mulesoft_client=MuleSoftMCPClient(os.getenv("MULESOFT_URL", ""), os.getenv("MULESOFT_USERNAME", ""), os.getenv("MULESOFT_PASSWORD", "")),
        confluence_client=ConfluenceMCPClient(os.getenv("CONFLUENCE_URL", ""), os.getenv("CONFLUENCE_USER", ""), os.getenv("CONFLUENCE_API_TOKEN", "")),
        journal_writer=JournalWriter(app_config.output_dir / "session_journal.json", secret_injector),
        request_executor=RequestExecutor(app_config.output_dir / "iteration_results.json"),
        secret_injector=secret_injector,
    )
    asyncio.run(orchestrator.run(log=lambda m: print(f"[progress] {m}")))
    ReportGenerator().generate(app_config.output_dir / "session_journal.json", app_config.output_dir / "report.html")
    print(f"Report generated: {app_config.output_dir / 'report.html'}")


if __name__ == "__main__":
    main()
