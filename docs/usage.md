# Usage

## Creating new shell

**shellfoundry** allows creating new shells based on templates. The below command-line will create a directory nutshell
and will initialize a shell skeleton based on base template. Base template structure is located at:
[https://github.com/QualiSystems/shellfoundry-template](https://github.com/QualiSystems/shellfoundry-template)

```bash
$ pip install new nutshell
```

## Creating new shell from custom template

**shellfoundry** also allows creation a new shell based on specific template. The below command-line will create a shell
according to specific template:

```bash
$ pip install new nutshell --template_name=base
```

## Listing available templates

**shellfoundry** displays list of available templates by executing the following command-line:
shellfoundry
```bash
$ shellfoundry list
```
In order to add a new template or modify exisging one, please refer to [Contributing](~contributing.md)

## Packaging a shell

**shellfoundry** allows to pack shell's source code, data model and configuration into a ZIP package.
It can be done using pack command:
```bash
$ shellfoundry pack
```
Pack command requires the presence of shell.yml file in the following structure:

###shell.yml
```yaml
 shell:
    name: nutshell
```
Pack command should be executed from the shell root folder where shell.yml is located. ZIP package will be created in
dist folder with name nutshell.zip . If your shell was created using **shellfoundry**, shell.yml file should exist.

## Installing a shell
Shell package can be installed into CloudShell using install command. It should be executed from shell's root folder as well.
```bash
$ shellfoundry install
```

Return to [Table of Contents](readme.md)
