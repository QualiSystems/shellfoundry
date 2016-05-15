# shellfoundry
Command line utility for CloudShell shells developers. The utility helps to create a new shell based on a template,
build an installable shell package and install a shell into your CloudShell.

## Installation

shellfoundry is available on the Pypi server and can be installed using:

```batch
> pip install shellfoundry
```

## Usage

### Creating a new shell based on template
**shellfoundry** allows creating a new fresh shell from scratch using template. The default shell template is located
in github repository  https://github.com/QualiSystems/shellfoundry-template
In order to create a shell from that github repository use the following command line:

```batch
> python shellfoundry create https://github.com/QualiSystems/shellfoundry-template.git
```
or using a shortcut:
```batch
> python shellfoundry create gh:QualiSystems/shellfoundry-template
```

Another option is to use your own template located on your local machine. In such case the following command-line
will do the magic:
```batch
> python shellfoundry create c:\shells\templates\my-template
```

Once created a shell you may push it to your github repository and develop it according to your needs.

### Building a shell package
Building a shell package allows installing it into your CloudShell. Use the following command line for building a shell.
The result of this operation will be a zip file named shell_name.zip, which can be imported into CloudShell using
drag-and-drop in the portal or install command of **shellfoundry**.

```batch
> python shellfoundry build shell_name
```

### Installing a shell package
In order to apply your shell onto your CloudShell, it needs to be installed. The following command-line will install
shell_name.zip into your CloudShell.

```batch
> python shellfoundry install shell_name
```

