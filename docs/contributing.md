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
$ git commit -am "changes"
$ git push
```
- Submit pull request



Return to [Table of Contents](readme.md)
