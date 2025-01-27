""" This module contains the FastAPI application that serves as the API for the DEM. """
# dem/api/main.py

from fastapi import HTTPException
from pydantic import BaseModel
from dem.core.platform import Platform
from dem.core.commands.run_cmd import execute as run_execute

platform: Platform | None = None

class RunCommandRequest(BaseModel):
    """ Request model for the run command. 

        Attributes:
            dev_env_name -- the name of the Development Environment to run the task in
            task_name -- the name of the task to run
            extra_args -- the arguments to pass to the task
    """
    dev_env_name: str
    task_name: str
    extra_args: str

@Platform.fastapi_app.post("/run")
def run_command(request: RunCommandRequest) -> dict:
    """ Run the given task in the given Development Environment.
    
        Args:
            request -- the request containing the Development Environment name, the task name, 
                        and the extra arguments
            
        Returns:
            a dictionary containing the status and message
    """
    dev_env_name = request.dev_env_name
    task_name = request.task_name
    extra_args = request.extra_args

    try:
        run_execute(platform, dev_env_name, task_name, extra_args)
        return {"status": "success", "message": f"Task {task_name} executed in {dev_env_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))