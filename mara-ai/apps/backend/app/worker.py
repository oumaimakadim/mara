import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows and activities
from app.workflows import GreetingWorkflow
from app.activities import say_hello

async def main():
    print("Connecting to Temporal server...")
    client = await Client.connect("temporal:7233")

    worker = Worker(
        client,
        task_queue="mara-tasks",
        workflows=[GreetingWorkflow],
        activities=[say_hello],
    )

    print("Worker started. Listening on 'mara-tasks'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
