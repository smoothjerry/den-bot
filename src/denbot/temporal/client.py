"""Factory for constructing a connected Temporal client.

Both the Discord bot process (to start workflows) and the worker process
(to poll task queues) acquire their client through ``get_client``.
"""

import asyncio
import logging
from pathlib import Path

from temporalio.client import Client, TLSConfig

from denbot.temporal.config import TemporalConfig

logger = logging.getLogger(__name__)

# Initial connection retry budget. temporalio/auto-setup takes 20-30s to
# bootstrap schema on first boot, so workers commonly race it. These defaults
# give us up to ~2 minutes of retries before giving up.
_INITIAL_BACKOFF_SECONDS = 1.0
_MAX_BACKOFF_SECONDS = 15.0
_DEFAULT_CONNECT_TIMEOUT_SECONDS = 120.0


async def get_client(
    config: TemporalConfig | None = None,
    *,
    connect_timeout_seconds: float = _DEFAULT_CONNECT_TIMEOUT_SECONDS,
) -> Client:
    """Connect to the Temporal server, retrying transient failures with backoff.

    Raises the last connection error if ``connect_timeout_seconds`` elapses
    without a successful connect.
    """
    config = config or TemporalConfig.from_env()

    tls: bool | TLSConfig = False
    if config.tls_enabled:
        tls = TLSConfig(
            client_cert=Path(config.tls_cert_path).read_bytes(),
            client_private_key=Path(config.tls_key_path).read_bytes(),
        )

    logger.info(
        "Connecting Temporal client: address=%s namespace=%s tls=%s",
        config.address,
        config.namespace,
        config.tls_enabled,
    )

    loop = asyncio.get_event_loop()
    deadline = loop.time() + connect_timeout_seconds
    backoff = _INITIAL_BACKOFF_SECONDS
    attempt = 0

    while True:
        attempt += 1
        try:
            return await Client.connect(
                config.address,
                namespace=config.namespace,
                tls=tls,
            )
        except RuntimeError as exc:
            # temporalio wraps transport errors from the Rust bridge as
            # RuntimeError. We retry anything that looks connection-shaped
            # and bubble up everything else immediately.
            if not _is_transient_connect_error(exc):
                raise
            remaining = deadline - loop.time()
            if remaining <= 0:
                logger.error(
                    "Temporal connect failed after %d attempts; giving up",
                    attempt,
                )
                raise
            wait = min(backoff, remaining)
            logger.warning(
                "Temporal connect attempt %d failed, retrying in %.1fs: %s",
                attempt,
                wait,
                exc,
            )
            await asyncio.sleep(wait)
            backoff = min(backoff * 2, _MAX_BACKOFF_SECONDS)


def _is_transient_connect_error(exc: BaseException) -> bool:
    message = str(exc).lower()
    return any(
        needle in message
        for needle in (
            "connection refused",
            "connectionrefused",
            "unavailable",
            "dns",
            "transport error",
        )
    )
