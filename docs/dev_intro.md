# Developer Intro

PyPDFForm is designed for Python developers. This documentation section is intended for contributors to PyPDFForm, not its end-users.

## Setup

To get started, create a virtual environment and install the development dependencies using your preferred package manager.

The command below uses [uv](https://docs.astral.sh/uv/):

```shell
uv pip install -r pyproject.toml --extra dev
```

PyPDFForm also offers a development container. To build it, run the following command in the project's root directory:

```shell
docker build -t pypdfform-dev .
```

Once successfully built, you can open a shell inside the container by running:

```shell
docker run -it --rm -p 8000:8000 -v ${PWD}:/pypdfform pypdfform-dev
```

## Running tests

See [testing PyPDFForm with pytest](dev_test.md).

## Creating issues

When creating a GitHub issue, follow these guidelines:

* The issue title should have the format `PPF-<issue number>: <title of the issue>`.
* The issue description should be as descriptive as possible, preferably with the following:
    * A code snippet related to the issue.
    * A PDF form template used by the code snippet.
    * Screenshots that can help visualize the issue.

## Opening pull requests

Before opening a pull request, create an issue. When opening the pull request, follow these guidelines:

* The PR title should be the same as its respective issue, so `PPF-<issue number>: <title of the issue>`.
* The PR description should contain a brief explanation of the changes.
* Once opened, the PR should be linked to its respective issue.
