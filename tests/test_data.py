dev_env_json = """{
    "version": "0.1",
    "development_environments": [{
            "name": "demo",
            "tools": [{
                    "type": "build system",
                    "image_name": "make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "cpputest",
                    "image_version": "latest"
                }
            ]
        },
        {
            "name": "nagy_cica_project",
            "tools": [{
                    "type": "build system",
                    "image_name": "bazel",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "jlink",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "jlink",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "cpputest",
                    "image_version": "latest"
                }
            ]
        }
    ]
}
"""

empty_dev_env_json = """{
    "version": "0.1",
    "development_environments": []
}
"""

invalid_dev_env_json = """{
	"version": "0.1",
	"development_environments": [{
			"name": "demo",
			"tools": [{
					"type": "build_system",
					"image_name": "make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "toolchain",
					"image_name": "make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "debugger",
					"image_name": "stlink_org",
					"image_version": "latest"
				},
				{
					"type": "deployer",
					"image_name": "stlink_org",
					"image_version": "latest"
				},
				{
					"type": "test framework",
					"image_name": "cpputest",
					"image_version": "latest"
				}
			]
		}
	]
}
"""