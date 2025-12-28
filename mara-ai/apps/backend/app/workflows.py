from datetime import timedelta
from temporalio import workflow

# Import activity definition
with workflow.unsafe.imports_passed_through():
    from app.activities import say_hello

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )
