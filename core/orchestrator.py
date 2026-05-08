"""Main orchestration loop for autonomous API testing sessions."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Callable, Optional

from config import AppConfig
from core.auth_manager import AuthManager
from core.journal_writer import JournalWriter
from core.models import ApiSpec, JournalEntry
from core.request_executor import RequestExecutor
from core.secret_injector import SecretInjector

logger = logging.getLogger(__name__)


@dataclass
class Orchestrator:
    """Coordinate MCP fetch, LLM command generation, execution, and journaling."""

    config: AppConfig
    llm_adapter: object
    mulesoft_client: object
    confluence_client: object
    journal_writer: JournalWriter
    request_executor: RequestExecutor
    secret_injector: SecretInjector
    stop_requested: bool = False

    async def run(self, log: Optional[Callable[[str], None]] = None) -> Path:
        """Run full autonomous session and return report path."""

        spec = await self._fetch_spec()
        spec_path = self.config.output_dir / "api_spec.json"
        spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

        for iteration in range(1, self.config.max_iterations + 1):
            if self.stop_requested:
                break
            prompt = self._build_prompt(spec_path, iteration)
            commands = self.llm_adapter.generate_commands(prompt, on_stream=log)
            injected = [self.secret_injector.inject(c) for c in commands]
            result_record = self.request_executor.execute_batch(iteration, injected)
            sanitized = [{**r.__dict__, "command": "[REDACTED]"} for r in result_record.results]
            entry = JournalEntry(
                timestamp=datetime.utcnow().isoformat(),
                iteration=iteration,
                claude_request=prompt,
                claude_analysis="Iteration completed",
                sanitized_responses=sanitized,
            )
            self.journal_writer.append(entry)
            if log:
                log(f"Iteration {iteration} completed with {len(sanitized)} requests")
        return self.config.output_dir / "report.html"

    async def _fetch_spec(self) -> dict:
        """Fetch and merge specs from MuleSoft and Confluence MCP sources."""

        await self.mulesoft_client.connect()
        await self.confluence_client.connect()
        try:
            mulesoft, confluence = await asyncio.gather(
                self.mulesoft_client.fetch_spec(), self.confluence_client.fetch_spec()
            )
            return {
                "fetched_at": datetime.utcnow().isoformat(),
                "sources": ["mulesoft", "confluence"],
                "mulesoft": mulesoft,
                "confluence": confluence,
            }
        finally:
            await self.mulesoft_client.disconnect()
            await self.confluence_client.disconnect()

    def stop(self) -> None:
        """Signal session stop after current safe checkpoint."""

        self.stop_requested = True

    @staticmethod
    def _build_prompt(spec_path: Path, iteration: int) -> str:
        """Construct command-generation prompt sent to Claude."""

        return (
            "You are an API test planner. Emit only a JSON array of curl commands using placeholders. "
            "Do not execute them. "
            f"Use spec from: {spec_path}. Iteration: {iteration}."
        )
