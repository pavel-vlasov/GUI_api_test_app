"""Configuration panel widgets for desktop UI."""
from __future__ import annotations

import customtkinter as ctk


class ConfigPanel(ctk.CTkFrame):
    """Config form for source URLs and auth inputs."""

    def __init__(self, master):
        """Initialize configuration panel."""

        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="MuleSoft URL").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.mulesoft_entry = ctk.CTkEntry(self, placeholder_text="https://anypoint.mulesoft.com/...")
        self.mulesoft_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="Confluence URL").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.confluence_entry = ctk.CTkEntry(self, placeholder_text="https://company.atlassian.net/wiki/...")
        self.confluence_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="Auth mode").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.auth_mode = ctk.CTkOptionMenu(self, values=["oauth", "static"])
        self.auth_mode.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="OAuth token URL").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        self.oauth_token_url = ctk.CTkEntry(self, placeholder_text="https://auth.example.com/oauth2/token")
        self.oauth_token_url.grid(row=3, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="OAuth client ID").grid(row=4, column=0, sticky="w", padx=8, pady=6)
        self.oauth_client_id = ctk.CTkEntry(self, placeholder_text="client-id")
        self.oauth_client_id.grid(row=4, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="OAuth client secret").grid(row=5, column=0, sticky="w", padx=8, pady=6)
        self.oauth_client_secret = ctk.CTkEntry(self, placeholder_text="client-secret", show="*")
        self.oauth_client_secret.grid(row=5, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="OAuth scopes").grid(row=6, column=0, sticky="w", padx=8, pady=6)
        self.oauth_scopes = ctk.CTkEntry(self, placeholder_text="scope1 scope2")
        self.oauth_scopes.grid(row=6, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="Static auth header").grid(row=7, column=0, sticky="w", padx=8, pady=6)
        self.static_auth_header = ctk.CTkEntry(self, placeholder_text="Bearer <token>")
        self.static_auth_header.grid(row=7, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(self, text="Max iterations").grid(row=8, column=0, sticky="w", padx=8, pady=6)
        self.max_iterations = ctk.CTkEntry(self, placeholder_text="3")
        self.max_iterations.insert(0, "3")
        self.max_iterations.grid(row=8, column=1, sticky="ew", padx=8, pady=6)

    def get_values(self) -> dict:
        """Return cleaned config values from the form."""

        return {
            "mulesoft_url": self.mulesoft_entry.get().strip(),
            "confluence_url": self.confluence_entry.get().strip(),
            "auth_mode": self.auth_mode.get(),
            "oauth_token_url": self.oauth_token_url.get().strip(),
            "oauth_client_id": self.oauth_client_id.get().strip(),
            "oauth_client_secret": self.oauth_client_secret.get().strip(),
            "oauth_scopes": self.oauth_scopes.get().strip(),
            "static_auth_header": self.static_auth_header.get().strip(),
            "max_iterations": self.max_iterations.get().strip(),
        }
