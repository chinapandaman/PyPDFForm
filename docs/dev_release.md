# Releasing

The PyPDFForm release process begins with the following steps:

* Creating a release [issue](https://github.com/chinapandaman/PyPDFForm/issues/686) and [PR](https://github.com/chinapandaman/PyPDFForm/pull/687).
* Publishing a new [GitHub release](https://github.com/chinapandaman/PyPDFForm/releases) with auto-generated changelogs.

After completing these steps, the deployment CI will be triggered.

## Versioning

PyPDFForm follows the conventions defined by [Semantic Versioning](https://semver.org/).

## Deploy process

Creating a GitHub release triggers two CIs:

* [Deploy](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-publish.yml), which will create the distribution and upload it to [PyPI](https://pypi.org/project/PyPDFForm/).
* [Deploy Docs](https://github.com/chinapandaman/PyPDFForm/actions/workflows/deploy-docs.yml), which will tear down and rebuild the [GitHub page](https://chinapandaman.github.io/PyPDFForm/) where the doc site is hosted.

## When are releases done?

The timing of releases depends on the changes pending deployment on the master branch. Generally:

* Serious bugs are usually released immediately after they are fixed.
* New features can usually wait and are released on a weekly basis.
* Trivial changes are usually bundled with other changes and can wait indefinitely.
