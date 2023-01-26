import os
import json

class DevEnv:
	supported_tool_types = ( 
		"build_system",
		"toolchain",
		"debugger",
		"deployer",
		"test_environment",
	)
	def __init__(self, name, tools):
		self.name = name
		self.tools = tools

	def print_info(self):
		print("Dev Env name: " + self.name )

if __name__ == "__main__":
	#Get the raw json file.
	dev_env_json_path = os.path.expanduser('~') + "/.config/axem/dev_env.json"
	dev_env_json = open(dev_env_json_path, "r")

	#Parse the json file.
	dev_env_json_deserialized = json.load(dev_env_json)

	print(dev_env_json_deserialized["version"])

	for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
		dev_env = DevEnv(dev_env_descriptor["name"], dev_env_descriptor["tools"])
		dev_env.print_info()