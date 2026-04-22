"""Temporal worker runner.

Workers are long-running processes that poll a task queue on the Temporal
server and execute registered workflows/activities. This module is invoked
by the ``denbot.worker`` entrypoint.
"""

import asyncio
import logging

from temporalio.worker import Worker

from denbot.temporal.activities import say_hello
from denbot.temporal.client import get_client
from denbot.temporal.config import TemporalConfig
from denbot.temporal.workflows import HelloWorkflow

logger = logging.getLogger(__name__)


async def run() -> None:
    config = TemporalConfig.from_env()
    client = await get_client(config)
    logger.info("Temporal worker starting task_queue=%s", config.task_queue)
    worker = Worker(
        client,
        task_queue=config.task_queue,
        workflows=[HelloWorkflow],
        activities=[say_hello],
    )
    await worker.run()


def main() -> None:
    asyncio.run(run())
