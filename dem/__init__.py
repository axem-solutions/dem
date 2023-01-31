"""Top-level package for dem."""
# dem/__init__.py

__app_name__ = "dem"
__version__ = "0.1.0"

(
	SUCCESS,
	DEV_EVN_JSON_ERROR,
) = range(2)

ERRORS = {
	DEV_EVN_JSON_ERROR: "Invalid dev_env.json file error"
}