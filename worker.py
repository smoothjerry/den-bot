import asyncio
import os

from temporalio.worker import Worker
from temporalio.client import Client
from workflows import HelloWorldWorkflow, say_hello

async def main():
    # Connect to the Temporal server
    client = await Client.connect(os.getenv("TEMPORAL", "temporal:7233"))  # Replace "temporal" with the Railway Temporal host if needed
    print("Connected to Temporal")

    # Start the worker
    worker = Worker(
        client,
        task_queue="hello-task-queue",  # Task queue name
        workflows=[HelloWorldWorkflow],
        activities=[say_hello],
    )
    print("Worker running...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
