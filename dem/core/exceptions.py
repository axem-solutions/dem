"""Collection of dem specific exceptions."""
# dem/core/exceptions.py

class InvalidDevEnvJson(Exception):
    "Raised when the dev_env.json file is invalid."

    def __init__(self, message: str):
        super().__init__(message)