# Pull Request Requirements

Whenever a pull request is submitted, there are some expectations for the content before it can be merged 
into the master branch.

## Code changes

There isn't any strict rule on how coding should be done for PyPDFForm. The project welcomes code contributions from 
anyone with any level of expertise.

With that said, there are some conventions that are expected to be followed by your PR:

* Small changes are preferred over lengthy changes. If your changes are large, please request a feature branch in your issue 
and open your PR against that branch, as your changes will likely need to be revised before merging into master.
* Your changes must pass [Pylint](https://www.pylint.org/). To check if this is true, simply run `pylint PyPDFForm`.
* Your changes must pass all tests and have 100% coverage. You can read more about testing [here](dev_test.md).
* If you are changing the user APIs or any other parts of the code that are relevant, please update the appropriate documentation too.

## Merge process

Your PR will be reviewed before merging into the master branch. On top of that, it needs to run through some CI checks:

* Pylint on the source code.
* Tests will be run on three mainstream operating systems: `ubuntu`, `windows`, and `macos`, and across all Python versions the library supports on each OS.

Once the CI is green and your code looks good, the PR will be merged into the master branch. After every PR merge, [black](https://black.readthedocs.io/) and 
[isort](https://pycqa.github.io/isort/) will be run on your code, and they will be deployed on the next release.