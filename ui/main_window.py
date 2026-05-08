"""Main CustomTkinter window with non-blocking orchestration controls."""
from __future__ import annotations

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

        self.start_button = ctk.CTkButton(controls, text="Start", command=start_callback)
        self.start_button.pack(side="left", padx=6)
        self.stop_button = ctk.CTkButton(controls, text="Stop", command=stop_callback, state="disabled")
        self.stop_button.pack(side="left", padx=6)
        self.report_button = ctk.CTkButton(controls, text="Open HTML Report", command=open_report_callback)
        self.report_button.pack(side="left", padx=6)

        self.bind_all("<Control-v>", self._paste_from_clipboard)
        self.bind_all("<Control-V>", self._paste_from_clipboard)
        self.bind_all("<Shift-Insert>", self._paste_from_clipboard)

    def _paste_from_clipboard(self, _event) -> str | None:
        """Insert clipboard text into currently focused entry/text widget."""

        focused = self.focus_get()
        if focused is None:
            return None
        try:
            focused.event_generate("<<Paste>>")
        except Exception:  # noqa: BLE001
            return None
        return "break"

    def set_running_state(self, is_running: bool) -> None:
        """Toggle controls based on active run state."""

        self.start_button.configure(state="disabled" if is_running else "normal")
        self.stop_button.configure(state="normal" if is_running else "disabled")
