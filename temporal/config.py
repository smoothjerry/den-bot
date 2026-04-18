"""Temporal client/worker configuration.

Reads connection details from environment variables. All fields have sensible
defaults for local development against a docker-compose Temporal stack.
"""

import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_ADDRESS = "localhost:7233"
DEFAULT_NAMESPACE = "default"
DEFAULT_TASK_QUEUE = "denjamin-main"


@dataclass(frozen=True)
class TemporalConfig:
    address: str = DEFAULT_ADDRESS
    namespace: str = DEFAULT_NAMESPACE
    task_queue: str = DEFAULT_TASK_QUEUE
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None

    @classmethod
    def from_env(cls) -> "TemporalConfig":
        return cls(
            address=os.getenv("TEMPORAL_ADDRESS", DEFAULT_ADDRESS),
            namespace=os.getenv("TEMPORAL_NAMESPACE", DEFAULT_NAMESPACE),
            task_queue=os.getenv("TEMPORAL_TASK_QUEUE", DEFAULT_TASK_QUEUE),
            tls_cert_path=os.getenv("TEMPORAL_TLS_CERT_PATH") or None,
            tls_key_path=os.getenv("TEMPORAL_TLS_KEY_PATH") or None,
        )

    @property
    def tls_enabled(self) -> bool:
        return bool(self.tls_cert_path and self.tls_key_path)
