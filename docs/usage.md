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

To create a new shell from different template version:

```bash
$ shellfoundry new nutshell --template networking/router --version <version_number>
```

To use the latest template, omit the --version option.

* To view all available versions of a given template, please refer to the *show* command.
** Please note that template versioning is only supported by tosca shells.

## Listing available templates

**shellfoundry** displays list of the available templates by executing the following command-line:

```bash
$ shellfoundry list
```

To view only relevant templates, use one of the available filter flags: --tosca, --legacy and --all
Default view is configurable using the *defaultview* key set to one of the following: tosca, legact or all. To set a config key refer to the *config* command section

* To add a new template or modify an existing one, please refer to [Contributing](../.github/contributing.md)

## Showing template versions

**shellfoundry** displays list of the versions for a given template by executing the following command-line:

```bash
$ shellfoundry show <template_name>
```

The versions will dispay in a descending order from latest down to earliest.

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

### Altering CloudShell connection configuration

To alter CloudShell connection information use the *config* command like so:

```bash
$ shellfoundry config <key> <value>
```

This will create a global configuration file inside %APPDATA%\Quali\shellfoundry (or equivilent on linux) and will act upon all shells to be installed
other than those with local configuration file (cloudshell_config.yml).

For times that a local configuration file is more suitable please use this command from shell's root folder:

```bash
$ shellfoundry --local config <key> <value>
```

To remove a key from the configuration simply use:

```bash
$ shellfoundry config --remove <key>
```

To view install configuration use this:

```bash
$ shellfoundry config
```

(in order to switch to local use the --local flag on shell's root folder)

* Replace <key> and <value> with the desired key and value to save into the configuration file.
* Configuration files are created once shellfoundry config (--global/--local flag) is executed.

Return to [Table of Contents](readme.md)
