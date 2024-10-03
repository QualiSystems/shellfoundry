#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

__all__ = [
    "TOSCA_META_LOCATION",
    "TEMPLATE_AUTHOR_FIELD",
    "TEMPLATE_VERSION",
    "TEMPLATE_BASED_ON",
    "CLOUDSHELL_MAX_RETRIES",
    "CLOUDSHELL_RETRY_INTERVAL_SEC",
    "DEFAULT_TIME_WAIT",
    "TEMPLATE_PROPERTY",
    "TEMPLATES_YML",
    "SERVER_VERSION_KEY",
]

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
TOSCA_META_LOCATION = os.path.join("TOSCA-Metadata", "TOSCA.meta")
SERVER_VERSION_KEY = "server_version"
