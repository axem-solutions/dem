""" This module contains the FastAPI application that serves as the API for the DEM. """
# dem/api/main.py
from fastapi import HTTPException
from pydantic import BaseModel
from dem.core.platform import Platform
from dem.core.commands.run_cmd import execute as run_execute

platform: Platform | None = None

class RunCommandRequest(BaseModel):
    dev_env_name: str
    task_name: str

@Platform.fastapi_app.post("/run")
def run_command(request: RunCommandRequest) -> dict:
    dev_env_name = request.dev_env_name
    task_name = request.task_name

    try:
        run_execute(platform, dev_env_name, task_name)
        return {"status": "success", "message": f"Task {task_name} executed in {dev_env_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))