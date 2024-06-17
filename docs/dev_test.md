# Testing

PyPDFForm uses [pytest](https://pytest.org/) for testing and [coverage.py](https://coverage.readthedocs.io/) 
for test coverages. Tests can be run by simply executing:

```shell
coverage run -m pytest && coverage report --fail-under=100
```

## Generate coverage report

To generate a coverage report, run:

```shell
coverage run -m pytest && coverage html
```

And the coverage report can be viewed by openning `htmlcov/index.html` in a browser.
