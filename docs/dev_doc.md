# Hosting Docs Locally

When the changes apply to the user APIs or any other parts of the code that are relevant, the appropriate documentation should 
also be updated.

PyPDFForm uses [MkDocs](https://www.mkdocs.org/) for building the documentation. To host the doc site locally, simply run:

```shell
mkdocs serve
```

And you will find the doc site at `http://127.0.0.1:8000/`.

Alternatively, in the development container:

```shell
docs
```

And you will find the doc site at `http://localhost:8000/`.
