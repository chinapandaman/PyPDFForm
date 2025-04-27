# Pull Request Requirements

When submitting a pull request, follow these guidelines for a smooth review process.

## Code changes

PyPDFForm welcomes contributions from developers of all levels and doesn't enforce strict coding rules.

Your PR should follow these conventions:

* Prefer small, incremental changes. For large changes, request a feature branch in your issue and open your PR against that branch, as they will likely need revision before merging into master.
* Ensure your changes pass all linters. PyPDFForm uses rules from [pylint](https://www.pylint.org/), [ruff](https://docs.astral.sh/ruff/), and [pyright](https://microsoft.github.io/pyright/#/). Run `linting` inside the development container to check.
* Your changes must pass all tests and have 100% coverage. You can read more about testing [here](dev_test.md).
* If you are changing the user APIs or any other parts of the code that are relevant, please update the appropriate documentation too.

## Merge process

Your PR will be reviewed before merging into the master branch. If your changes are too extensive for inline comments, you may need to reopen your PR against a new feature branch for revision.

Additionally, your PR must pass these CI checks:

* [Linting](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-linting.yml) on the source code.
* [Tests](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml) will be run on three mainstream operating systems: `ubuntu`, `windows`, and `macos`, and across all Python versions the library supports on each OS.

Once the CI is green and your code looks good, the PR will be merged into the master branch. They will be deployed on the next release.
