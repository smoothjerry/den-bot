from temporalio import workflow, activity
from datetime import timedelta

# Define the activity
@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

# Define the workflow
@workflow.defn
class HelloWorldWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Call the activity
        return await workflow.execute_activity(
            say_hello,
            name,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
