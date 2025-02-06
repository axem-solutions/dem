"""Collection of dem specific exceptions."""
# dem/core/exceptions.py

class DataStorageError(Exception):
    """Raised when valid data can't be loaded from file."""

    base_message = "Invalid file: "

    def __init__(self, message: str = "") -> None:
        super().__init__(self.base_message + message)

class RegistryError(Exception):
    """Raised when the communication with registry fails."""

    base_message = "Registry error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class ToolImageError(Exception):
    """Raised when there is a problem with the tool image."""
    pass

class ContainerEngineError(Exception):
    """Raised when there is a problem with the container engine."""

    base_message = "Container engine error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class InternalError(Exception):
    """Raised when an object is used incorrectly."""
    pass

class PlatformError(Exception):
    """Raised when there is a problem with the platform."""

    base_message = "Platform error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class CatalogError(Exception):
    """Raised when there is a problem with the catalog."""

    base_message = "Catalog error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class TaskError(Exception):
    """ Raised when there is a problem with a task. """

    base_message = "Task error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)

class DevEnvError(Exception):
    """ Raised when there is a problem with a Development Environment. """

    base_message = "Development Environment error: "

    def __init__(self, message: str) -> None:
        super().__init__(self.base_message + message)