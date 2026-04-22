"""Temporal workflow definitions.

Workflows must be deterministic: no wall-clock time, no random numbers,
no direct IO. They orchestrate activities, which do the real work.
"""

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from denbot.temporal.activities import say_hello


@workflow.defn
class HelloWorkflow:
    """Starter workflow: calls ``say_hello`` and returns its result."""

    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
