"""Configuration helpers for the PTY flight pipeline.

This module keeps environment variables explicit and testable. It does not load
or expose secrets in public documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime configuration loaded from environment variables."""

    rapidapi_key: str
    gmail_user: str
    gmail_app_password: str
    email_to: str
    dry_run: bool = False


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_config(*, dry_run: bool = False) -> RuntimeConfig:
    """Load runtime configuration from the environment."""

    return RuntimeConfig(
        rapidapi_key=_required_env("RAPIDAPI_KEY"),
        gmail_user=_required_env("GMAIL_USER"),
        gmail_app_password=_required_env("GMAIL_APP_PASSWORD"),
        email_to=_required_env("EMAIL_TO"),
        dry_run=dry_run,
    )
