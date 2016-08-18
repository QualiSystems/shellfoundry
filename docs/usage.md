# Usage

## Creating new shell

**shellfoundry** allows creating new shells based on templates. The below command-line creates a directory *nutshell*
and initializes a shell skeleton based on the *base* template. The structure of the *base* template is located at:
[https://github.com/QualiSystems/shellfoundry-template](https://github.com/QualiSystems/shellfoundry-template)

```bash
$ shellfoundry new nutshell
```

## Creating new shell from custom template

**shellfoundry** also allows creating a new shell based on a specific template. The below command-line creates
a shell that is based on a specific template:

```bash
$ shellfoundry new nutshell --template networking/router
```

## Listing available templates

**shellfoundry** displays list of the available templates by executing the following command-line:

```bash
$ shellfoundry list
```
To add a new template or modify an existing one, please refer to [Contributing](../.github/contributing.md)

## Packaging a shell

**shellfoundry** allows packing the shell's source code, data model and configuration into a ZIP package.
Use the *pack* command todo this:

```bash
$ shellfoundry pack
```
The *pack* command requires the presence of *shell.yml* file in the following structure:

###shell.yml
```yaml
 shell:
    name: nutshell
```
Pack should be executed from the shell root folder where the *shell.yml* is located. A ZIP package is created in
the *dist* directory with the name *"nutshell.zip"*. If your shell was created using **shellfoundry**, the *shell.yml* file should exist.

## Installing a shell
The shell package can be installed into CloudShell using the *install* command. Please execute it from the shell's root folder

```bash
$ shellfoundry install
```

Return to [Table of Contents](readme.md)
