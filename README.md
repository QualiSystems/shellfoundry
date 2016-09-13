# shellfoundry

[![Join the chat at https://gitter.im/QualiSystems/shellfoundry](https://badges.gitter.im/QualiSystems/shellfoundry.svg)](https://gitter.im/QualiSystems/shellfoundry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/QualiSystems/shellfoundry.svg?branch=develop)](https://travis-ci.org/QualiSystems/shellfoundry) [![Coverage Status](https://coveralls.io/repos/github/QualiSystems/shellfoundry/badge.svg?branch=develop)](https://coveralls.io/github/QualiSystems/shellfoundry?branch=develop) [![PyPI](https://img.shields.io/pypi/pyversions/shellfoundry.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/v/shellfoundry.svg?maxAge=2592000)]()
[![Dependency Status](https://dependencyci.com/github/QualiSystems/shellfoundry/badge)](https://dependencyci.com/github/QualiSystems/shellfoundry)

Command line utility for CloudShell shells developers. The utility helps to create a new shell based on a template,
build an installable shell package and install a shell into your CloudShell.

# Installation

1. Choose a TOSCA template

| $ shellfoundry list   |
|-----------------------|

2. Create a shell

| $ shellfoundry new `<shell`> --template `<template`>  |
|-------------------------------------------------------|


| $ cd `<shell`> |
|----------------|

3. Define data model in shell-definition.yml
4. Generate data model

| $ shellfoundry generate  |
|--------------------------|

5. Implement logic in driver.py using classes from data_model.py
6. Install the shell package into Cloudshell

|  $ shellfoundry install   |
|---------------------------|



# Additional Links

- For more commands and detailed usage please refer to [Documentation](docs/readme.md)

- Opening issues and feature requests: [Issue Tracker](https://github.com/QualiSystems/shellfoundry/issues)

- Forum for questions and discussions: [Gitter.im](https://gitter.im/QualiSystems/shellfoundry)

# License
[Apache License 2.0](https://github.com/QualiSystems/shellfoundry/blob/master/LICENSE)


