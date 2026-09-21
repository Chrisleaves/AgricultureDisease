from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class AppConfig:
    api_url: str
    api_timeout: int

    @classmethod
    def load(cls, secrets: Mapping[str, Any] | None = None) -> "AppConfig":
        secrets = secrets or {}
        api_url = str(
            secrets.get("DIAGNOSIS_API_URL")
            or os.getenv("DIAGNOSIS_API_URL", "http://127.0.0.1:8000")
        ).rstrip("/")
        timeout_value = secrets.get("DIAGNOSIS_API_TIMEOUT") or os.getenv(
            "DIAGNOSIS_API_TIMEOUT", "120"
        )
        try:
            timeout = max(5, int(timeout_value))
        except (TypeError, ValueError):
            timeout = 120
        return cls(api_url=api_url, api_timeout=timeout)

