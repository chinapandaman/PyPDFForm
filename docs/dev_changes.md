# Pull Request Requirements

When submitting a pull request, certain expectations must be met before it can be merged into the master branch.

## Code changes

PyPDFForm doesn't have strict coding rules, welcoming contributions from developers of all expertise levels.

With that said, there are some conventions that are expected to be followed by your PR:

* Small, incremental changes are preferred. For large changes, request a feature branch in your issue and open your PR against that branch, as they will likely require revision before merging into master.
* Your changes must pass all the linters. PyPDFForm uses a combined set of rules from [pylint](https://www.pylint.org/), [ruff](https://docs.astral.sh/ruff/), and [pyright](https://microsoft.github.io/pyright/#/). To check if your code passes all the linters, simply run `linting` inside the development container.
* Your changes must pass all tests and have 100% coverage. You can read more about testing [here](dev_test.md).
* If you are changing the user APIs or any other parts of the code that are relevant, please update the appropriate documentation too.

## Merge process

Your PR will undergo review before being merged into the master branch. If your changes are too extensive for inline review comments, you may be asked to reopen your PR against a new feature branch for revision and refactoring.

On top of that, your PR needs to run through some CI checks:

* [Linting](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-linting.yml) on the source code.
* [Tests](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml) will be run on three mainstream operating systems: `ubuntu`, `windows`, and `macos`, and across all Python versions the library supports on each OS.

Once the CI is green and your code looks good, the PR will be merged into the master branch. They will be deployed on the next release.
