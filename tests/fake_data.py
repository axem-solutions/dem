dev_env_json = """{
    "version": "0.1",
    "development_environments": [{
            "name": "demo",
            "tools": [{
                    "type": "build system",
                    "image_name": "axemsolutions/make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/cpputest",
                    "image_version": "latest"
                }
            ]
        },
        {
            "name": "nagy_cica_project",
            "tools": [{
                    "type": "build system",
                    "image_name": "axemsolutions/bazel",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/jlink",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/jlink",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/cpputest",
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
					"image_name": "axemsolutions/make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "toolchain",
					"image_name": "axemsolutions/make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "debugger",
					"image_name": "axemsolutions/stlink_org",
					"image_version": "latest"
				},
				{
					"type": "deployer",
					"image_name": "axemsolutions/stlink_org",
					"image_version": "latest"
				},
				{
					"type": "test framework",
					"image_name": "axemsolutions/cpputest",
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
                    "image_name": "axemsolutions/cmake",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/llvm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/unity",
                    "image_version": "latest"
                }
            ]
        },
        {
            "name": "demo",
            "tools": [{
                    "type": "build system",
                    "image_name": "axemsolutions/make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/make_gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/stlink_org",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/cpputest",
                    "image_version": "latest"
                }
            ]
        },
        {
            "name": "nagy_cica_project",
            "tools": [{
                    "type": "build system",
                    "image_name": "axemsolutions/bazel",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/gnu_arm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/jlink",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/jlink",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/cpputest",
                    "image_version": "latest"
                }
            ]
        },
        {
            "name": "unavailable_image_env",
            "tools": [{
                    "type": "build system",
                    "image_name": "axemsolutions/unavailable_build_system_image",
                    "image_version": "latest"
                },
                {
                    "type": "toolchain",
                    "image_name": "axemsolutions/llvm",
                    "image_version": "latest"
                },
                {
                    "type": "debugger",
                    "image_name": "axemsolutions/pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "deployer",
                    "image_name": "axemsolutions/pemicro",
                    "image_version": "latest"
                },
                {
                    "type": "test framework",
                    "image_name": "axemsolutions/unity",
                    "image_version": "latest"
                }
            ]
        }
    ]
}"""

empty_dev_env_org_json = """{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": []
}"""