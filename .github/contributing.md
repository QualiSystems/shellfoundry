# Contributing

## Adding modifying/shell template
Shell templates are github repositories in a specific format. The base shell template is located at
[https://github.com/qualisystems/shellfoundry-template](https://github.com/qualisystems/shellfoundry-template).

To add a new template, fork the above template and modify it as needed. The shell template are based on the
cookiecutter command-line utility, which is used for creating projects based on templates.
Please refer to its documentation at: [http://cookiecutter.readthedocs.io/en/latest/](http://cookiecutter.readthedocs.io/en/latest/)

Once a new template repository is created, you will need to add it to the list of templates located at:
[templates.yml](../templates.yml)

###templates.yml
```yaml
templates:
    - name : base
      description : Base shell template
      repository : https://github.com/QualiSystems/shellfoundry-template
```

See the instructions below to learn how you can contribute to **shellfoundry**


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
      - Write a failing test first
      - Write a minimum amount of code to satisfy the failing test
      - Refactor the code

    - Running tests from command line:
    ```bash
    $ python setup.py test
    ```

- Commit and push them to github
```bash
$ git add .
$ git commit -m "Your detailed description of your changes"
$ git push origin name-of-your-feature
```
- Submit a pull request

## Pull Request Guidelines

Before you submit a pull request, make sure it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function
with a docstring, and add the feature to the list in [Usage](usage.md]
3. The pull request should support for Python 2.7. Check https://travis-ci.org/QualiSystems/shellfoundry and make sure that the tests pass for all supported Python versions.


Return to [Table of Contents](readme.md)
