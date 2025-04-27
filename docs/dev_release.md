# Releasing

The PyPDFForm release process involves these initial steps:

1. A [version bump commit](https://github.com/chinapandaman/PyPDFForm/commit/71b4983d115819d413edfdfc83af57f95ad292c7) that runs [black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) on the codebase.
2. A new [GitHub release](https://github.com/chinapandaman/PyPDFForm/releases) with auto-generated changelogs.

These steps trigger the deployment CI.

## Versioning

PyPDFForm follows the conventions defined by [Semantic Versioning](https://semver.org/).

## Deploy process

A GitHub release triggers two CIs:

* [Deploy](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-publish.yml), which will create the distribution and upload it to [PyPI](https://pypi.org/project/PyPDFForm/).
* [Deploy Docs](https://github.com/chinapandaman/PyPDFForm/actions/workflows/deploy-docs.yml), which will tear down and rebuild the [GitHub page](https://chinapandaman.github.io/PyPDFForm/) where the doc site is hosted.

## When are releases done?

Release timing depends on changes pending deployment on the master branch. Generally:

* Serious bugs are usually released immediately after they are fixed.
* New features can usually wait and are released on a weekly basis.
* Trivial changes are usually bundled with other changes and can wait indefinitely.
