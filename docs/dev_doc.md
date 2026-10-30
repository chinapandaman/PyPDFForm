# Hosting Docs Locally

For guidance on when to update the User Guide and how to word changes, see the [pull request requirements](dev_changes.md#code-changes).

PyPDFForm uses [MkDocs](https://www.mkdocs.org/) to build its documentation. You can either host it locally in a virtual environment or run it in the development container.

=== "Virtual Environment"
    To host the documentation locally, run:
    ```shell
    mkdocs serve -a 0.0.0.0:8080
    ```

=== "Development Container"
    Alternatively, to run the documentation in the development container:
    ```shell
    docs
    ```

The documentation will be available at [http://localhost:8080/](http://localhost:8080/).
