from __future__ import annotations

from os.path import dirname, join

# GENERAL SECTION
ALTERNATIVE_TEMPLATES_PATH = join(dirname(__file__), "data", "templates.yml")
ALTERNATIVE_STANDARDS_PATH = join(dirname(__file__), "data", "standards.json")
MASTER_BRANCH_NAME = "master"
PACKAGE_NAME = __package__.split(".")[0]

# UTILITIES SECTION
CLOUDSHELL_MAX_RETRIES = 5
CLOUDSHELL_RETRY_INTERVAL_SEC = 0.5
DEFAULT_TIME_WAIT = 1.0
METADATA_AUTHOR_FIELD = "Created-By"
TEMPLATE_AUTHOR_FIELD = "metadata/template_author"
TEMPLATE_VERSION = "metadata/template_version"
TEMPLATE_BASED_ON = "metadata/template_based_on"
TEMPLATE_INFO_FILE = "cookiecutter.json"
TEMPLATE_PROPERTY = {
    "type": "string",
    "default": "fast",
    "description": "Some attribute description",
    "constraints": [{"valid_values": ["fast", "slow"]}],
}
TEMPLATES_YML = (
    "https://raw.github.com/QualiSystems/shellfoundry/master/templates_v1.yml"
)
TOSCA_META_LOCATION = join("TOSCA-Metadata", "TOSCA.meta")
SERVER_VERSION_KEY = "server_version"
