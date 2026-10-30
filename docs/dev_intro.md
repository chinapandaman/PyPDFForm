# Developer Intro

PyPDFForm is a project built with Python. This part of the documentation is specifically for those who want to contribute to the project's development.

## Setup

=== "Virtual Environment"
    To get started, create a virtual environment and install the development dependencies using your preferred package manager.

    The command below uses [uv](https://docs.astral.sh/uv/):

    ```shell
    uv pip install -U -r pyproject.toml --all-extras
    ```
=== "Development Container"
    PyPDFForm also offers a development container. It uses the median of the five supported Python versions, currently Python 3.13. To build it, run the following command in the project's root directory:

    ```shell
    docker build -t pypdfform-dev .
    ```

    Once successfully built, you can open a shell inside the container by running:

    ```shell
    docker run -it --rm -p 8000:8000 -p 8080:8080 -v .:/pypdfform pypdfform-dev
    ```

## Running tests

See [testing PyPDFForm with pytest](dev_test.md).

## Creating issues

When creating a GitHub issue, follow these guidelines:

* Create the issue with a descriptive title, then update it to `PPF-<issue number>: <title of the issue>` using the number assigned by GitHub. The issue number is only available after creation.
* The issue description should be as descriptive as possible, preferably with the following:
    * A code snippet related to the issue.
    * A PDF form template used by the code snippet.
    * Screenshots that can help visualize the issue.

## Opening pull requests

Before opening a pull request, create an issue. When opening the pull request, follow these guidelines:

* The PR title should match its respective issue: `PPF-<issue number>: <title of the issue>`. The prefix uses the linked issue's number, so it can be set when opening the PR.
* The PR description should contain a brief explanation of the changes.
* Once opened, the PR should be linked to its respective issue.
