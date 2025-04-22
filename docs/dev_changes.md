# Pull Request Requirements

When submitting a pull request, certain expectations must be met before it can be merged into the master branch.

## Code changes

PyPDFForm doesn't have strict coding rules, welcoming contributions from developers of all expertise levels.

With that said, there are some conventions that are expected to be followed by your PR:

* Small, incremental changes are preferred. For large changes, request a feature branch in your issue and open your PR against that branch, as they will likely require revision before merging into master.
* Your changes must pass [Pylint](https://www.pylint.org/). To check if this is true, simply run `pylint PyPDFForm`.
* Your changes must pass all tests and have 100% coverage. You can read more about testing [here](dev_test.md).
* If you are changing the user APIs or any other parts of the code that are relevant, please update the appropriate documentation too.

## Merge process

Your PR will undergo review before being merged into the master branch. If your changes are too extensive for inline review comments, you may be asked to reopen your PR against a new feature branch for revision and refactoring.

On top of that, your PR needs to run through some CI checks:

* Pylint on the source code.
* Tests will be run on three mainstream operating systems: `ubuntu`, `windows`, and `macos`, and across all Python versions the library supports on each OS.

Once the CI is green and your code looks good, the PR will be merged into the master branch. After every PR merge, [black](https://black.readthedocs.io/) and 
[isort](https://pycqa.github.io/isort/) will be run on your code, and they will be deployed on the next release.