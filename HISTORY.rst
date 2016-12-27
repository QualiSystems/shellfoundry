=======
History
=======

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

* Fixed a bug in config command which caused shellfoundry to crash when config file has not existed

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
