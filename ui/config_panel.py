"""Configuration panel widgets for desktop UI."""
from __future__ import annotations

import customtkinter as ctk


class ConfigPanel(ctk.CTkFrame):
    """Config form for source URLs and auth inputs."""

    def __init__(self, master):
        """Initialize configuration panel."""

        super().__init__(master)
        self.mulesoft_entry = ctk.CTkEntry(self, placeholder_text="MuleSoft URL")
        self.confluence_entry = ctk.CTkEntry(self, placeholder_text="Confluence URL")
        self.auth_mode = ctk.CTkOptionMenu(self, values=["oauth", "static"])
        for w in (self.mulesoft_entry, self.confluence_entry, self.auth_mode):
            w.pack(fill="x", padx=8, pady=6)
