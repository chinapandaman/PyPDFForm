# Hosting Docs Locally

When making changes to user APIs or other significant parts of the code, it's important to also update the relevant documentation.

PyPDFForm uses [MkDocs](https://www.mkdocs.org/) to build its documentation. You can host it locally in a virtual environment or run it in the development container.

## Host from virtual environment

To host the documentation locally, run:

```shell
mkdocs serve
```

The documentation will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Host from development container

Alternatively, to run the documentation in the development container:

```shell
docs
```

The documentation will be available at [http://localhost:8000/](http://localhost:8000/).
