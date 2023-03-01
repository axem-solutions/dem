"""Collection of dem specific exceptions."""
# dem/core/exceptions.py

class InvalidDevEnvJson(Exception):
    "Raised when the dev_env.json file is invalid."

    base_message = "Error in dev_env.json: "

    def __init__(self, message: str):
        super().__init__(self.base_message + message)