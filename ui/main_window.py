"""Main CustomTkinter window with non-blocking orchestration controls."""
from __future__ import annotations

import queue
import threading
import customtkinter as ctk

from ui.config_panel import ConfigPanel
from ui.log_panel import LogPanel


class MainWindow(ctk.CTk):
    """Desktop application window for API testing orchestrator."""

    def __init__(self, start_callback, stop_callback, open_report_callback):
        """Create UI components and wire control callbacks."""

        super().__init__()
        self.title("Autonomous API Tester")
        self.geometry("1000x700")
        self.config_panel = ConfigPanel(self)
        self.config_panel.pack(fill="x", padx=12, pady=8)
        self.log_panel = LogPanel(self)
        self.log_panel.pack(fill="both", expand=True, padx=12, pady=8)
        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(controls, text="Start", command=start_callback).pack(side="left", padx=6)
        ctk.CTkButton(controls, text="Stop", command=stop_callback).pack(side="left", padx=6)
        ctk.CTkButton(controls, text="Open HTML Report", command=open_report_callback).pack(side="left", padx=6)
