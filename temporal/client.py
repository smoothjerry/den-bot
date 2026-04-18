"""Factory for constructing a connected Temporal client.

Both the Discord bot process (to start workflows) and the worker process
(to poll task queues) acquire their client through ``get_client``.
"""

import logging
from pathlib import Path
from typing import Optional

from temporalio.client import Client, TLSConfig

from temporal.config import TemporalConfig

logger = logging.getLogger(__name__)


async def get_client(config: Optional[TemporalConfig] = None) -> Client:
    """Connect to the Temporal server described by ``config`` (or env)."""
    config = config or TemporalConfig.from_env()

    tls: "bool | TLSConfig" = False
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
    return await Client.connect(
        config.address,
        namespace=config.namespace,
        tls=tls,
    )
