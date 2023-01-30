import os
import json

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

	def debug_print(self):
		print("Dev Env name: " + self.descriptor["name"] )
		print("Available tools: ")

		for tool in self.descriptor["tools"]:
			print("\tType\t\t\t: " + tool["type"])
			print("\tToolinfo\t\t: " + tool["tool_info"])
			print("\tImage name\t\t: " + tool["image_name"])
			print("\tImage version\t\t: " + tool["image_version"])

if __name__ == "__main__":
	#Get the raw json file.
	dev_env_json_path = os.path.expanduser('~') + "/.config/axem/dev_env.json"
	dev_env_json = open(dev_env_json_path, "r")

	#Parse the json file.
	dev_env_json_deserialized = json.load(dev_env_json)

	print("dev_env.json version: " + dev_env_json_deserialized["version"])
	print("\r\n")

	for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
		dev_env = DevEnv(dev_env_descriptor)
		dev_env.debug_print()