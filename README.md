# shellfoundry

[![Join the chat at https://gitter.im/QualiSystems/shellfoundry](https://badges.gitter.im/QualiSystems/shellfoundry.svg)](https://gitter.im/QualiSystems/shellfoundry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/QualiSystems/shellfoundry.svg?branch=develop)](https://travis-ci.org/QualiSystems/shellfoundry) [![Coverage Status](https://coveralls.io/repos/github/QualiSystems/shellfoundry/badge.svg?branch=develop)](https://coveralls.io/github/QualiSystems/shellfoundry?branch=develop) [![PyPI](https://img.shields.io/pypi/pyversions/shellfoundry.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/v/shellfoundry.svg?maxAge=2592000)]()

Command line utility for CloudShell shells developers. The utility helps to create a new shell based on a template,
build an installable shell package and install a shell into your CloudShell.

## Installation

shellfoundry is available on the Pypi server and can be installed using:

```batch
> pip install shellfoundry
```

## Usage

### Displaying version
```batch
> shellfoundry version
```

### Displaying availbale templates
Lists available templates
```batch
> shellfoundry list
```

### Creating a new shell based on template
**shellfoundry** allows creating a new fresh shell from scratch using template. In order to create a shell based on a default template use the following command line:
```batch
>  shellfoundry new nutshell
```

In order to create a shell based on specific template
```batch
> shellfoundry new nutshell --template_name=template_name
```
Once created a shell you may push it to your github repository and develop it according to your needs.

### Packaging a shell
Packaging a shell package creates a ZIP representing the sell. Zipped shell package can be installed into your CloudShell.
```batch
> cd nutshell
> shellfoundry pack
```

### Installing a shell package
In order to apply your shell onto your CloudShell, it needs to be installed. The following command-line will install
shell_name.zip into your CloudShell.

```batch
> shellfoundry install
```

