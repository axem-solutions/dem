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
invalid_version_dev_env_json = """{
    "version": "1.0"
}"""

dev_env_org_json = """{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": [{
            "name": "org_only_env",
            "tools": [{
                    "type": "build system",
                    "image_name": "cmake",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "llvm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "unity",
                    "image_version": "latest"
                }
            ]
        }
    ]
}"""