# shellfoundry
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
>  shellfoundry new --name=nutshell
```

In order to create a shell based on specific template
or using a shortcut:
```batch 
> shellfoundry new --name=nutshell --template=template_name
```
Once created a shell you may push it to your github repository and develop it according to your needs.

### Building a shell package
Building a shell package allows installing it into your CloudShell. Use the following command line for building a shell.
The result of this operation will be a zip file named shell_name.zip, which can be imported into CloudShell using
drag-and-drop in the portal or install command of **shellfoundry**.

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

