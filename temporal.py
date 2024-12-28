import os

from temporalio.client import Client

async def main():
    # Replace with your Temporal service's address from Railway
    temporal_host = os.getenv("TEMPORAL")

    # Connect to Temporal server
    client = await Client.connect(temporal_host)

    # Example: Start a workflow
    result = await client.execute_workflow(
        "example_workflow",
        "Hello, Temporal!",
        id="example-workflow-id",
        task_queue="example-task-queue",
    )
    print(f"Workflow result: {result}")

# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
