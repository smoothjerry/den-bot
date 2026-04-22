"""Temporal activities.

Activities are plain async functions executed by a worker. They're where
side effects and non-deterministic code live (network calls, DB writes, etc.).
"""

from temporalio import activity


@activity.defn
async def say_hello(name: str) -> str:
    """Starter activity used to smoke-test the Temporal stack end-to-end."""
    activity.logger.info("say_hello invoked name=%s", name)
    return f"Hello, {name}!"
