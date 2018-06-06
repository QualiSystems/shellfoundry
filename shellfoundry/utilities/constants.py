#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

__all__ = ["TOSCA_META_LOCATION", "TEMPLATE_AUTHOR_FILED", "TEMPLATE_VERSION", "TEMPLATE_BASED_ON",
           "CLOUDSHELL_MAX_RETRIES", "CLOUDSHELL_RETRY_INTERVAL_SEC", "DEFAULT_TIME_WAIT", "TEMPLATE_PROPERTY"]

TOSCA_META_LOCATION = os.path.join("TOSCA-Metadata", "TOSCA.meta")
METADATA_AUTHOR_FIELD = "Created-By"
TEMPLATE_AUTHOR_FIELD = "metadata/template_author"
TEMPLATE_VERSION = "metadata/template_version"
TEMPLATE_BASED_ON = "metadata/template_based_on"
TEMPLATE_INFO_FILE = "cookiecutter.json"

CLOUDSHELL_MAX_RETRIES = 5
CLOUDSHELL_RETRY_INTERVAL_SEC = 0.5
DEFAULT_TIME_WAIT = 1.0

TEMPLATE_PROPERTY = {"type": "string",
                     "default": "fast",
                     "description": "Some attribute description",
                     "constraints": [{"valid_values": ["fast", "slow"]}]
                     }
