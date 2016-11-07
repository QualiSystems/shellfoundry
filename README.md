[![Join the chat at https://gitter.im/QualiSystems/shellfoundry](https://badges.gitter.im/QualiSystems/shellfoundry.svg)](https://gitter.im/QualiSystems/shellfoundry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/QualiSystems/shellfoundry.svg?branch=develop)](https://travis-ci.org/QualiSystems/shellfoundry) [![Coverage Status](https://coveralls.io/repos/github/QualiSystems/shellfoundry/badge.svg?branch=develop)](https://coveralls.io/github/QualiSystems/shellfoundry?branch=develop) [![PyPI](https://img.shields.io/pypi/pyversions/shellfoundry.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/v/shellfoundry.svg?maxAge=2592000)]()
[![Dependency Status](https://dependencyci.com/github/QualiSystems/shellfoundry/badge)](https://dependencyci.com/github/QualiSystems/shellfoundry)

---

![quali](quali.png)

# ShellFoundry CLI

Command line utility for *Shells Developers* of our **CloudShell** platform.  It helps in creating a new shell based on a template, build an installable shell package and install a shell into your **CloudShell** instance.

## Why use ShellFoundry?

* To show list of available shell templates
* To create a new shell based on an existing template
* To generate Python classes based on your data model, either XML or TOSCA YAML
* To package a shell
* To create set of dependencies for offline usage
* To import a shell into your **CloudShell**
* To publish a shell on Quali Community


## Installing


```
$ python -m pip install shellfoundry
```

## Basic Usage

```
$ shellfoundry new nutshell
```

> For detailed usage information refer to [this guide](docs/usage.md)


## Troubleshooting and Help

For questions, bug reports or feature requests, please refer to the [Issue Tracker](https://github.com/QualiSystems/shellfoundry/issues).  Also, make sure you check out our [Issue Template](.github/issue_template.md).

## Contributing


All your contributions are welcomed and encouraged.  We've compiled detailed information about:

* [Contributing](.github/contributing.md)
* [Creating Pull Requests](.github/pull_request_template.md)


## Dependencies

Development of **ShellFoundry** would not have been possible without the open source libraries it depends on:

- [cookiecutter](https://github.com/audreyr/cookiecutter)
- [requests](http://docs.python-requests.org/)
- [click](http://click.pocoo.org/5/)
- [pyyaml](http://pyyaml.org/)

## License
[Apache License 2.0](https://github.com/QualiSystems/shellfoundry/blob/master/LICENSE)
