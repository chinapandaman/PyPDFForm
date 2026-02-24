# Releasing

The PyPDFForm release process involves these initial steps:

1. A [version bump commit](https://github.com/chinapandaman/PyPDFForm/commit/97ccaa34e7ee48d69fd3807ccd93c0af5ef8869d) that runs [black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) on the codebase.
2. A new [GitHub release](https://github.com/chinapandaman/PyPDFForm/releases) with auto-generated changelogs.

These steps trigger the deployment CI.

## Versioning

PyPDFForm follows [Semantic Versioning](https://semver.org/).

Documentation versioning follows a slightly different strategy, tracking only major and minor versions. For example, a release of `v1.2.3` updates the documentation for `v1.2`, whereas a release of `v1.3.0` creates documentation for `v1.3`.

## Deploy process

A GitHub release triggers two CIs:

* [Deploy](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-publish.yml), which creates the distribution and uploads it to [PyPI](https://pypi.org/project/PyPDFForm/).
* [Deploy Docs](https://github.com/chinapandaman/PyPDFForm/actions/workflows/deploy-docs.yml), which updates the [doc site](https://chinapandaman.github.io/PyPDFForm/) or creates a new version for minor/major releases.

## When are releases done?

Release timing depends on changes pending deployment on the master branch. Generally:

* Serious bugs are usually released immediately after they are fixed.
* New features can usually wait and are released on a weekly basis.
* Trivial changes are usually bundled with other changes and can wait indefinitely.
