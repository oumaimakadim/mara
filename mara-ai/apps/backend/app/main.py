from fastapi import FastAPI
from temporalio.client import Client
import os

app = FastAPI(title="Mara AI Mission OS")

@app.get("/")
async def root():
    return {"message": "Mara AI Mission OS is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/mission/start")
async def start_mission(name: str):
    # Connect to Temporal
    client = await Client.connect("temporal:7233")
    
    # Execute Workflow
    handle = await client.start_workflow(
        "GreetingWorkflow",
        name,
        id=f"mission-{name}",
        task_queue="mara-tasks",
    )
    
    return {"mission_id": handle.id, "run_id": handle.run_id}
