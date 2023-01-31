"""This module represents the Development Environments."""
# dem/dev_env.py

class DevEnv:
	supported_tool_types = ( 
		"build_system",
		"toolchain",
		"debugger",
		"deployer",
		"test_framework",
	)

	def _check_tool_type_support(self, descriptor):
		for tool in descriptor["tools"]:
			if tool["type"] not in self.supported_tool_types:
				raise LookupError("The following tool type is not supported: " + tool["type"])

	def __init__(self, descriptor):
		self._check_tool_type_support(descriptor)
		self.name = descriptor["name"]
		self.tools = descriptor["tools"]

	def validate(self, images):
		checked_images = {}
		for tool in self.tools:
			if tool["image_name"] in images:
				checked_images[tool["image_name"]] = "present"
			else:
				checked_images[tool["image_name"]] = "missing"
		return checked_images

class DevEnvSetup:
	def __init__(self, dev_env_json_deserialized):
		self.version = dev_env_json_deserialized["version"]
		self.dev_envs = []

		for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
			self.dev_envs.append(DevEnv(dev_env_descriptor))