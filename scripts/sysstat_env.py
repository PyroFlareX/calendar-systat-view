"""Shared settings loader for the eww-sysstat poll scripts.

Settings come from, in order of precedence:
  1. the process environment (so `KEY=value eww ...` still works),
  2. the file named by $EWW_SYSSTAT_ENV, or `.env` next to eww.yuck.

Nothing in eww.yuck or the scripts embeds an endpoint or credential.
"""
from __future__ import annotations

import os
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    # Allow trailing comments on unquoted values: KEY=value # note
    return value.split(" #", 1)[0].rstrip()


def env_path() -> Path:
    override = os.environ.get("EWW_SYSSTAT_ENV")
    return Path(override).expanduser() if override else CONFIG_DIR / ".env"


def load() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = env_path().read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        lines = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if sep and key.isidentifier():
            values[key] = _unquote(value)
    for key, value in os.environ.items():
        values[key] = value
    return values


def get(settings: dict[str, str], key: str, default: str = "") -> str:
    value = settings.get(key, "").strip()
    return value or default
