"""Live log panel for streaming backend output."""
from __future__ import annotations

import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """Read-only scrollable text log panel."""

    def __init__(self, master):
        """Initialize log panel."""

        super().__init__(master)
        self.text = ctk.CTkTextbox(self, height=350)
        self.text.pack(fill="both", expand=True)

    def append(self, message: str) -> None:
        """Append line into log panel."""

        self.text.insert("end", message + "\n")
        self.text.see("end")
