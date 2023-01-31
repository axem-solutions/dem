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
		self.descriptor = descriptor

	def validate(self, images):
		pass

	def debug_print(self):
		print("Dev Env name: " + self.descriptor["name"] )
		print("Available tools: ")

		for tool in self.descriptor["tools"]:
			print("\tType\t\t\t: " + tool["type"])
			print("\tToolinfo\t\t: " + tool["tool_info"])
			print("\tImage name\t\t: " + tool["image_name"])
			print("\tImage version\t\t: " + tool["image_version"])

class DevEnvSetup:
	def __init__(self, dev_env_json_deserialized):
		self.version = dev_env_json_deserialized["version"]
		self.dev_envs = []

		for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
			self.dev_envs.append(DevEnv(dev_env_descriptor))