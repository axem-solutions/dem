""" Uvircorn server for the FastAPI based DEM API. """
# dem/api/server.py

import uvicorn
from uvicorn._types import ASGIApplication
from typing import Callable, Any
from threading import Thread

class APIServer():
    """ Uvicorn server for the FastAPI based DEM API. """

    def __init__(self, app: ASGIApplication | Callable[..., Any] | str) -> None:
        """ Initialize the APIServer. 
        
            Args:
                app: the FastAPI application to run in the server.
        """
        config: uvicorn.Config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        self.server: uvicorn.Server = uvicorn.Server(config)
        self.thread: Thread = Thread(target=self._server_run_in_thread)

    def _server_run_in_thread(self) -> None:
        """ Run the server in a thread. """
        self.server.run()

    def start(self) -> None:
        """ Start the server. """
        self.thread.start()

    def stop(self) -> None:
        """ Stop the server. """
        self.server.handle_exit(None, None)
        self.thread.join()