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
        self.text.configure(state="disabled")

    def append(self, message: str) -> None:
        """Append line into log panel."""

        self.text.configure(state="normal")
        self.text.insert("end", message + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self) -> None:
        """Clear all text from log panel."""

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
