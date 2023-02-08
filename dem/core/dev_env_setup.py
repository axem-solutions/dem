"""This module represents the Development Environments."""
# dem/dev_env.py

class DevEnv:
	supported_tool_types = ( 
		"build system",
		"toolchain",
		"debugger",
		"deployer",
		"test framework",
	)

	def _check_tool_type_support(self, descriptor: dict):
		for tool in descriptor["tools"]:
			if tool["type"] not in self.supported_tool_types:
				raise LookupError("Error in dev_env.json. The following tool type is not supported: " + tool["type"])

	def __init__(self, descriptor: dict):
		self._check_tool_type_support(descriptor)
		self.name = descriptor["name"]
		self.tools = descriptor["tools"]

	def validate(self, local_images: list):
		for tool in self.tools:
			tool_image = tool["image_name"] + ':' + tool["image_version"]
			if tool_image in local_images:
				tool["is_image_available"] = True
			else:
				tool["is_image_available"] = False

class DevEnvSetup:
	def __init__(self, dev_env_json_deserialized: dict):
		self.version = dev_env_json_deserialized["version"]
		self.dev_envs = []

		for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
			self.dev_envs.append(DevEnv(dev_env_descriptor))