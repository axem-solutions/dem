"""Collection of dem specific exceptions."""
# dem/core/exceptions.py

class InvalidDevEnvJson(Exception):
    """Raised when the dev_env.json file is invalid."""

    base_message = "Error in dev_env.json: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class RegistryError(Exception):
    """Raised when the communication with registry fails."""
    pass

class ContainerEngineError(Exception):
    """Raised when there is a problem with the container engine."""

    base_message = "Container engine error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)