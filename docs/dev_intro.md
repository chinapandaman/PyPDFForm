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
    PyPDFForm also offers a development container. It uses the median of the five supported Python versions, currently Python 3.13. Its base images are pinned to digests, which Dependabot updates weekly, and it installs the newest dependency versions when built. To build it, run the following command in the project's root directory:

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

## Issue triage

Maintainers, meaning the repository owner and collaborators, triage issues. They decide:

* Whether a report is a confirmed defect, a feature or roadmap request, or needs more information.
* Whether a change to documented Python API or CLI behavior is acceptable, and which [version](dev_release.md#versioning) releases it.
* When an issue is closed. Confirmed defects and roadmap decisions stay open until they are fixed or a maintainer closes them with a reason.

Report vulnerabilities through a security advisory as described in the [security policy](https://github.com/chinapandaman/PyPDFForm/blob/master/SECURITY.md), not in an issue.

When a maintainer needs more information, they ask for it in a comment and add the `awaiting response` label. A nightly job closes a labeled issue once 30 days have passed since the label was added or a maintainer last commented, whichever is later. A comment from anyone else pauses this until a maintainer comments again, and the maintainer removes the label once the issue no longer needs a response. The job closes issues as not planned, with a comment saying the issue was not resolved. Comment with the requested information and a maintainer will reopen it. The job never closes pull requests or issues without the label.

To preview what the job would do without changing anything, run:

```shell
python scripts/close_staled_issues.py
```

## Opening pull requests

Before opening a pull request, create an issue. When opening the pull request, follow these guidelines:

* The PR title should match its respective issue: `PPF-<issue number>: <title of the issue>`. The prefix uses the linked issue's number, so it can be set when opening the PR.
* The PR description should contain a brief explanation of the changes.
* Once opened, the PR should be linked to its respective issue.
