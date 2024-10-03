=======
History
=======
1.2.25 (2024-07-30)
-------------------

* Added support for the latest cloudshell-rest-api
* Added possibility to pack shell without src folder

1.2.22 (2022-09-05)
-------------------

* Set default Python version for new Shells to "3"

1.2.21 (2022-03-31)
-------------------

* Fixed issue with list command in offline mode
* Fixed GH issue "Uninformative error message when configured domain is incorrect #254"
* Fixed GH issue "'Error' word repeats twice #251"

1.2.20 (2021-08-19)
-------------------

* Fixed password decryption error

1.2.19 (2021-07-27)
-------------------

* Fixed encoding issue

1.2.18 (2021-04-14)
-------------------

* Fixed encoding issue

1.2.17 (2020-02-12)
-------------------

* Fixed error with click and cookiecutter versions incompatibility
* Fixed multiple traceback issues

1.2.16 (2020-01-02)
-------------------

* Fixed error with click and cookiecutter versions incompatibility
* Fixed multiple traceback issues


1.2.13 (2019-10-18)
-------------------

* Fixed password modification error

1.2.11 (2019-08-14)
-------------------

* Added Python 3 support

1.2.10 (2019-04-22)
-------------------

* Added setuptools to requirements
* Changed setuptools import according to the latest version

1.2.9 (2019-03-27)
------------------

* Added possibility to download dependencies from local CS repository during 'shellfoundry dist' command

1.2.8 (2019-03-05)
------------------

* Fixed issue with wrong setuptools import

1.2.7 (2019-02-12)
------------------

* Fixed issue in "generate" command after renaming root folder

1.2.6 (2019-01-30)
------------------

* Added "get_templates" command
* Added "delete" command
* Removed driver zip-file after pack command
* Added generating shell documentation based on the template

1.2.5 (2018-10-04)
------------------

* Set strict python version

1.2.4 (2018-09-26)
------------------

* Removed unnecessary cloudshell-automation-api dependency from requirements
* Set static version for package click in requirements. click==6.7

1.2.2 (2018-08-16)
------------------

* Fixed bug in verification template and standards compatibility

1.2.1 (2018-08-13)
------------------

* Added dynamical determination of minimal CloudShell version from templates

1.2.0 (2018-07-26)
------------------

* Extended the "new" command behaviour for offline mode
* Added verification is template and standard version are compatible

1.1.9 (2018-05-03)
------------------

* Added offline mode functionality

1.1.8 (2018-04-23)
------------------

* Fixed typo in pack command behaviour
* Added new online template for Cloud Provider

1.1.7 (2018-04-03)
------------------

* Shellfoundry will now pack deployment options if exists
* Modified unpack method logic in extended command

1.1.6 (2018-03-27)
------------------

* Added limitation installing a gen2 shell(regular/service) into a non global domain

1.1.5 (2018-03-01)
------------------

* Added new online template for Traffic Generator Controller Service

1.1.4 (2018-02-21)
------------------

* Added new online template for Traffic Generator Chassis 2 Generation

1.1.2 (2018-01-09)
------------------

* Fixed extend command logic (unzip driver archive)

1.1.1 (2017-11-14)
------------------

* Added new online templates
* Added specific error message to Layer 1 Shells pack and install commands

1.1.0 (2017-10-30)
------------------

* Added author field to shellfoundry configuration
* Added extend command behavior
* Added verification when upgrading an official shell to unofficial

1.0.4 (2017-08-28)
------------------

* Fixed some inconsistencies between update and add shell specifically around the shell name

1.0.3 (2017-06-28)
------------------

* list command aborts if there is a new major version on pypi
* old shellfoundry versions are NOT supported anymore.
  Please use `pip install shellfoundry -U` in order to upgrade to the newest version

1.0.2 (2017-06-27)
------------------

* new command aborts if there is a new major version on pypi

1.0.1 (2017-06-26)
------------------

* new command now conforms to CloudShell naming rules

1.0.0 (2017-06-19)
------------------

* Please upgrade to this version as from now on, older versions will be obsolete
* list command will now show templates that are installable on your cloudshell
* new command will now create the latest version of the template that match the standards installed on your cloudshell
* When invoking new or list commands, there will be a notification in the case of a new shellfoundry version

0.2.7 (2017-05-16)
------------------

* Shellfoundry will now pack categories.xml if exists

0.2.6 (2017-03-14)
------------------

* Fixed some minor bugs

0.2.2 (2017-01-22)
------------------

* gen2/resource is the now the default template for new command instead of gen1/resource

0.2.0 (2017-01-17)
------------------

* List command filtering parameters have changed (legacy => gen1, tosca => gen2)
* Added another filtering parameter --layer1
* Minimum CloudShell version column appears on list command output table
* gen2 is now the default view for list command

0.1.3 (2016-12-27)
------------------

* shellfoundry config will now echo all default configuration if not override by user

0.1.2 (2016-12-26)
------------------

* Config command will now encrypt password field

0.1.0 (2016-12-14)
------------------

* Show command was added to view all available versions of a template
* A new option was added to the 'new' command. Please welcome --version. It enables template versioning on shellfoundry.

0.0.44 (2016-12-12)
-------------------

* Fixed a bug in config command which caused shellfoundry to crash when config file was missing

0.0.43 (2016-12-11)
-------------------

* List command is now able to filter results based on shell type (--tosca, --legacy, --all)

0.0.41 (2016-12-08)
-------------------

* Config command was added to allow setting configuration once for all shells in addition to local configuration

0.0.39 (2016-10-09)
-------------------

* Pack Shell icon if specified in shell-definition.yml file under metadata\template_icon for TOSCA based shells

0.0.38 (2016-09-28)
-------------------

* Update reference to cloudshell-rest-api 7.2.0.7 to use PUT method in update shell

0.0.35 (2016-09-15)
-------------------

* TOSCA support was added to pack and install commands
* Generate command was added that generates driver data model in Python

0.0.32 (2016-08-10)
-------------------

* Pack command downloads dependencies into dist directory
* Dependency for git was removed
* Local shell templates are supported
* Proxy support was added for access to github

0.0.31 (2016-08-04)
-------------------

* git prerequisite was removed. shellfoundry works without git being preinstalled

0.0.28 (2016-07-07)
-------------------

* Installation of package into CloudShell was fixed


0.0.26 (2016-06-23)
-------------------

* Images copied to the DataModel folder (Issue #21)

0.0.17 (2016-05-25)
-------------------

* Proper error message when install command fails in logging in into CloudShell

0.0.1 (2016-05-02)
------------------

* First release on PyPI.
