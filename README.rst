shellfoundry
============

**Create, Innovate and Automate with ShellFoundry**

|Chat| |BuildStatus| |CoverageStatus| |PyVersion| |PyPI| |DependencyStatus|

Command line utility for CloudShell shells developers. The utility helps
to create a new shell based on a template, build an installable shell
package and install a shell into your CloudShell.

Installation
============

.. code:: bash

    $ pip install shellfoundry

Usage
=====

ShellFoundry streamlines the whole process of shell development from choosing a template, via code generation and
installation.

1. Choose a TOSCA template

.. code:: bash

    $ shellfoundry list

2. Create a shell

.. code:: bash

    $ shellfoundry new <shell> –-template <template>
    $ cd <shell>

3. Define data model in shell-definition.yml
4. Generate data model

.. code:: bash

    $ shellfoundry generate

5. Implement logic in driver.py using classes from data\_model.py
6. Install the shell package into Cloudshell

.. code:: bash

    $ shellfoundry install

Additional Links
================

-  For more commands and detailed usage please refer to `Documentation`_

-  Opening issues and feature requests: `Issue Tracker`_

-  Forum for questions and discussions: `Gitter.im`_

License
=======

`Apache License 2.0`_

.. _Documentation: docs/readme.md
.. _Issue Tracker: https://github.com/QualiSystems/shellfoundry/issues
.. _Gitter.im: https://gitter.im/QualiSystems/shellfoundry
.. _Apache License 2.0: https://github.com/QualiSystems/shellfoundry/blob/master/LICENSE

.. |Chat| image:: https://badges.gitter.im/QualiSystems/shellfoundry.svg
   :target: https://gitter.im/QualiSystems/shellfoundry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |BuildStatus| image:: https://travis-ci.org/QualiSystems/shellfoundry.svg?branch=develop
   :target: https://travis-ci.org/QualiSystems/shellfoundry
.. |CoverageStatus| image:: https://coveralls.io/repos/github/QualiSystems/shellfoundry/badge.svg?branch=develop
   :target: https://coveralls.io/github/QualiSystems/shellfoundry?branch=develop
.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/shellfoundry.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/shellfoundry
.. |PyPI| image:: https://img.shields.io/pypi/v/shellfoundry.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/shellfoundry
.. |DependencyStatus| image:: https://dependencyci.com/github/QualiSystems/shellfoundry/badge
   :target: https://dependencyci.com/github/QualiSystems/shellfoundry






