# Contributing

## Adding modifying/shell template
Shell templates are github repositories in specific format. Base shell template is located at
[https://github.com/qualisystems/shellfoundry-template](https://github.com/qualisystems/shellfoundry-template).

In order to add a new template, for the above template and modify it as needed. Shell template are based on
cookicutter command-line utility, that is used for creating projects based on templates.
Please refer to its documentation: [http://cookiecutter.readthedocs.io/en/latest/](http://cookiecutter.readthedocs.io/en/latest/)

Once created a new template repository, it's required to add it to list of templates located at:
[templates.yml](../templates.yml)

In order to modify it, see instrucions below on how to contribute to **shellfoundry**


## Contributing to shellfoundry

- Fork **shellfoundry** repository to [QualiSystemsLab](https://github.com/qualisystemslab) or to your own account.
- Clone it to your local machine using

```bash
$ git clone https://github.com/YOUR_ACCOUNT/shellfoundry.git
```

- Create a branch for local development
```bash
$ git checkout -b name-of-your-feature
```

- Make the required changes:
    - It's important to use to keep high standard of code, so please develop using TDD:
    ### TDD
      - Write failing test first
      - Write minimum amount of code to satisfy the failing test
      - Refactor the code

    - Running tests from command line:
    ```bash
    $ python setup.py test
    ```

- Commit & push them to github
```bash
$ git add .
$ git commit -m "Your detailed description of your changes"
$ git push origin name-of-your-feature
```
- Submit pull request

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function
with a docstring, and add the feature to the list in [Usage](usage.md]
3. The pull request should work for Python 2.7. Check https://travis-ci.org/QualiSystems/shellfoundry and make sure that the tests pass for all supported Python versions.


Return to [Table of Contents](readme.md)
