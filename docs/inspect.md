# Inspect form field data

Once a PDF form is prepared, PyPDFForm can help you inspect its fields to determine the data needed to fill it. Several inspection methods are available to choose from.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

The CLI examples pipe JSON output through `jq` for readability.

## Generate a JSON schema that describes a PDF form

PyPDFForm can describe the data needed to fill a PDF form as a JSON schema:

=== "Library"
    ```python
    import json
    from PyPDFForm import PdfWrapper

    pdf_form_schema = PdfWrapper("sample_template.pdf").schema

    print(json.dumps(pdf_form_schema, indent=4, sort_keys=True))
    ```
=== "CLI"
    ```shell
    pypdfform inspect schema sample_template.pdf | jq
    ```
=== "Output"
    ```json
    {
        "additionalProperties": false,
        "properties": {
            "check": {
                "type": "boolean"
            },
            "check_2": {
                "type": "boolean"
            },
            "check_3": {
                "type": "boolean"
            },
            "test": {
                "type": "string"
            },
            "test_2": {
                "type": "string"
            },
            "test_3": {
                "type": "string"
            }
        },
        "type": "object"
    }
    ```

In this example, `sample_template.pdf` contains three text fields (`test`, `test_2`, and `test_3`) of type `string` and three checkboxes (`check`, `check_2`, and `check_3`) of type `boolean`.

You can use the PyPDFForm-generated JSON schema to validate the data used for filling a PDF form.

## Inspect PDF form data

To inspect the current values in a filled PDF form, use the `.data` attribute. For example, the following snippet inspects the values in [this PDF](pdfs/sample_template_filled.pdf):

=== "Library"
    ```python
    import json
    from PyPDFForm import PdfWrapper

    current_data = PdfWrapper("sample_template_filled.pdf").data

    print(json.dumps(current_data, indent=4, sort_keys=True))
    ```
=== "CLI"
    ```shell
    pypdfform inspect data sample_template_filled.pdf | jq
    ```
=== "Output"
    ```json
    {
        "check": true,
        "check_2": true,
        "check_3": true,
        "test": "test",
        "test_2": "test2",
        "test_3": "test3"
    }
    ```

## Generate sample data

PyPDFForm can also generate sample fill data for a PDF form:

=== "Library"
    ```python
    import json
    from PyPDFForm import PdfWrapper

    sample_data = PdfWrapper("sample_template.pdf").sample_data

    print(json.dumps(sample_data, indent=4, sort_keys=True))
    ```
=== "CLI"
    ```shell
    pypdfform inspect sample sample_template.pdf | jq
    ```
=== "Output"
    ```json
    {
        "check": true,
        "check_2": true,
        "check_3": true,
        "test": "test",
        "test_2": "test_2",
        "test_3": "test_3"
    }
    ```
