"""Integration tests for Temporal workflows.

Uses WorkflowEnvironment's time-skipping test server (bundled with the
temporalio SDK). No docker containers required — runs in a subprocess.
"""

import uuid

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal.activities import say_hello
from temporal.workflows import HelloWorkflow


@pytest.mark.asyncio
async def test_hello_workflow_end_to_end():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        task_queue = f"test-{uuid.uuid4()}"
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[HelloWorkflow],
            activities=[say_hello],
        ):
            result = await env.client.execute_workflow(
                HelloWorkflow.run,
                "Denjamin",
                id=f"hello-{uuid.uuid4()}",
                task_queue=task_queue,
            )

    assert result == "Hello, Denjamin!"
