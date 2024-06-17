# Developer Intro

PyPDFForm's targeted users are other Python developers. This section of the documentation is not for the users, 
but for people who want to start making contributions to PyPDFForm itself.

## Installing requirements

It is advised that a virtual environment is created before running this command:

```shell
pip install -r requirements.txt
```

## Running tests

See [testing PyPDFForm with pytest](dev_test.md)

## Creating issues

When you create an issue on GitHub, try your best to follow these conventions:

* The issue title should have the format `PPF-<issue number>: <title of the issue>`.
* The issue description should be as descriptive as possible, preferably with the following:
    * A code snippet related to the issue.
    * A PDF form template used by the code snippet.
    * Screenshots that can help visualize the issue.

## Openning pull requests

Please create an issue before making a pull request. Try your best to follow these conventions when do so:

* The PR title should be the same as its respective issue, so `PPF-<issue number>: <title of the issue>`.
* The PR description should contain a brief explanation on the changes.
* Once opened, the PR should be linked to its respective issue.
