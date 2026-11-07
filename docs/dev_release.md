# Releasing

The PyPDFForm release process involves these initial steps:

1. A [version bump commit](https://github.com/chinapandaman/PyPDFForm/commit/97ccaa34e7ee48d69fd3807ccd93c0af5ef8869d) that bumps the version and formats the codebase with [ruff](https://docs.astral.sh/ruff/).
2. A new [GitHub release](https://github.com/chinapandaman/PyPDFForm/releases) with auto-generated changelogs.

These steps trigger the deployment CI.

The [Create Release](https://github.com/chinapandaman/PyPDFForm/actions/workflows/create-release.yml) workflow releases the exact commit it runs on, which must be on `master`. It first runs the [Tests](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml) and [Linting](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-linting.yml) workflows on that commit, and creates nothing if any of their jobs fail. The version bump commit skips CI when it is pushed, so this is where it is first checked. The version at that commit must be the next patch, minor, or major version after the latest tag. The workflow creates the version's tag at that commit before the release, and stops if the tag already points at another commit. Rerunning it after the release exists creates nothing and succeeds.

## Versioning

PyPDFForm follows [Semantic Versioning](https://semver.org/).

Documentation versioning follows a slightly different strategy, tracking only major and minor versions. For example, a release of `v1.2.3` updates the documentation for `v1.2`, whereas a release of `v1.3.0` creates documentation for `v1.3`.

## Deploy process

A GitHub release triggers two CIs:

* [Deploy](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-publish.yml), which checks the release commit and uploads its distribution to [PyPI](https://pypi.org/project/PyPDFForm/).
* [Deploy Docs](https://github.com/chinapandaman/PyPDFForm/actions/workflows/deploy-docs.yml), which updates the [doc site](https://chinapandaman.github.io/PyPDFForm/) or creates a new version for minor/major releases.

Deploy runs the Tests and Linting workflows again on the release commit. Besides the test matrix, Tests builds the sdist and wheel once and checks them with `scripts/check_dist.py`:

* The file names, package metadata, installed `__version__`, and release tag name the same version.
* Both files contain exactly the expected files from the release commit, byte for byte. Apart from package files and metadata, the sdist only contains `README.md`, `LICENSE`, `pyproject.toml`, and top-level `tests/test*.py` files.
* On the oldest and newest supported Python versions, the wheel is installed into new environments outside the checkout, once without extras and once with the `cli` extra. PyPDFForm must import from the installed wheel rather than the checkout, and a form is created, filled, and reopened. The `pypdfform` command must show installation guidance without the `cli` extra, and create, fill, and inspect a form with it.

Deploy uploads those same files only if every Tests and Linting job passes and their SHA-256 checksums match the checked ones. The run summary records the commit and checksums. If anything fails, nothing is uploaded, but the GitHub release, its tag, and the docs already exist. Rerun the failed jobs if the failure was temporary. Otherwise, fix the problem on `master` and release the next version.

To rehearse a deployment, run the Deploy workflow manually on any branch. It runs every check and skips the upload.

To check a distribution locally, commit your changes, since files are compared with `HEAD`, then run:

```shell
rm -rf dist && uv build
python scripts/check_dist.py dist
```

The check uses the Python running the script. Pass `--python` once per version to check others, for example `--python 3.11 --python 3.15`.

## When are releases done?

Release timing depends on changes pending deployment on the master branch. Generally:

* Serious bugs are usually released immediately after they are fixed.
* New features can usually wait and are released on a weekly basis.
* Trivial changes are usually bundled with other changes and can wait indefinitely.
