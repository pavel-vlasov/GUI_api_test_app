"""Production-ready GUI runner wiring UI controls to orchestration."""
from __future__ import annotations

import asyncio
import os
import threading
import webbrowser
from pathlib import Path

from config import AppConfig, OAuthConfig, SourceConfig, load_env
from core.journal_writer import JournalWriter
from core.orchestrator import Orchestrator
from core.report_generator import ReportGenerator
from core.request_executor import RequestExecutor
from core.secret_injector import SecretInjector
from llm.claude_cli_adapter import ClaudeCliAdapter
from mcp.confluence_mcp import ConfluenceMCPClient
from mcp.mulesoft_mcp import MuleSoftMCPClient
from ui.main_window import MainWindow


class GuiController:
    """Controller object for UI event handlers and background execution."""

    def __init__(self, env_file: str = ".env", output_dir: str = "storage") -> None:
        load_env(env_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.orchestrator: Orchestrator | None = None
        self.window = MainWindow(self.start_run, self.stop_run, self.open_report)

    def start_run(self) -> None:
        """Validate UI settings and launch orchestration on background thread."""

        values = self.window.config_panel.get_values()
        if not values["mulesoft_url"] or not values["confluence_url"]:
            self.window.log_panel.append("ERROR: MuleSoft URL and Confluence URL are required.")
            return

        try:
            max_iterations = int(values["max_iterations"])
            if max_iterations < 1:
                raise ValueError
        except ValueError:
            self.window.log_panel.append("ERROR: Max iterations must be a positive integer.")
            return

        oauth = OAuthConfig(
            token_url=os.getenv("TOKEN_URL", ""),
            client_id=os.getenv("CLIENT_ID", ""),
            client_secret=os.getenv("CLIENT_SECRET", ""),
            scopes=os.getenv("SCOPES", "").split(),
        ) if values["auth_mode"] == "oauth" else None

        cfg = AppConfig(
            auth_mode=values["auth_mode"],
            oauth=oauth,
            sources=SourceConfig(values["mulesoft_url"], values["confluence_url"]),
            output_dir=self.output_dir,
            max_iterations=max_iterations,
        )

        secret_injector = SecretInjector({"<TOKEN>": os.getenv("API_TOKEN", ""), "<API_KEY>": os.getenv("API_KEY", "")})
        self.orchestrator = Orchestrator(
            config=cfg,
            llm_adapter=ClaudeCliAdapter(),
            mulesoft_client=MuleSoftMCPClient(values["mulesoft_url"], os.getenv("MULESOFT_USERNAME", ""), os.getenv("MULESOFT_PASSWORD", "")),
            confluence_client=ConfluenceMCPClient(values["confluence_url"], os.getenv("CONFLUENCE_USER", ""), os.getenv("CONFLUENCE_API_TOKEN", "")),
            journal_writer=JournalWriter(self.output_dir / "session_journal.json", secret_injector),
            request_executor=RequestExecutor(self.output_dir / "iteration_results.json"),
            secret_injector=secret_injector,
        )

        self.window.log_panel.clear()
        self.window.set_running_state(True)
        threading.Thread(target=self._run_async, daemon=True).start()

    def _run_async(self) -> None:
        """Run async pipeline and publish progress safely back to UI thread."""

        try:
            asyncio.run(self.orchestrator.run(log=self._post_log))
            ReportGenerator().generate(self.output_dir / "session_journal.json", self.output_dir / "report.html")
            self._post_log(f"Report generated: {self.output_dir / 'report.html'}")
        except Exception as exc:  # noqa: BLE001
            self._post_log(f"ERROR: {exc}")
        finally:
            self.window.after(0, lambda: self.window.set_running_state(False))

    def _post_log(self, message: str) -> None:
        """Post a log line to the text panel from any thread."""

        self.window.after(0, lambda: self.window.log_panel.append(message))

    def stop_run(self) -> None:
        """Request stop for currently running orchestrator."""

        if self.orchestrator:
            self.orchestrator.stop()
            self.window.log_panel.append("Stop requested. Finishing current iteration...")

    def open_report(self) -> None:
        """Open generated report in default browser if present."""

        report = self.output_dir / "report.html"
        if report.exists():
            webbrowser.open(report.resolve().as_uri())
        else:
            self.window.log_panel.append("Report not found yet. Run a session first.")


def main() -> None:
    """Launch desktop GUI app."""

    controller = GuiController()
    controller.window.mainloop()


if __name__ == "__main__":
    main()
