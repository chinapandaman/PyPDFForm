# Inspect form field data

Once a PDF form is prepared, PyPDFForm can help you inspect its fields to determine the data needed to fill it. Several inspection methods are available to choose from.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

## Generate a JSON schema that describes a PDF form

You can describe the dictionary used to fill a PDF form using a JSON schema. For example:

=== "Code"
    ```python
    import json
    from PyPDFForm import PdfWrapper

    pdf_form_schema = PdfWrapper("sample_template.pdf").schema

    print(json.dumps(pdf_form_schema, indent=4, sort_keys=True))
    ```
=== "Output"
    ```json
    {
        "additionalProperties": true,
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

To inspect the current filled data of a PDF form, use the `.data` attribute. For example, the following snippet inspects the current filled data for [this PDF](pdfs/sample_template_filled.pdf):

=== "Code"
    ```python
    from pprint import pprint
    from PyPDFForm import PdfWrapper

    pprint(PdfWrapper("sample_template_filled.pdf").data)
    ```
=== "Output"
    ```sh
    {'check': True,
    'check_2': True,
    'check_3': True,
    'test': 'test',
    'test_2': 'test2',
    'test_3': 'test3'}
    ```

## Inspect individual form field widgets

The `.widgets` attribute gives you a dictionary mapping each field name to its widget object. Each widget exposes properties such as `name`, `value`, `page_number`, `x`, `y`,`width`,`height`,`tooltip`,`readonly`,`required`, and`hidden`.

You can iterate over all widgets to see their types and current state:

=== "Code"
    ```python
    from pprint import pprint
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")

    pprint(pdf.widgets)
    ```
=== "Output"
    ```sh
   {'check': Checkbox(name='check', value=None, readonly=False, required=False, hidden=False, page_number=1, x=358.874, y=664.717, width=18.47999999999996, height=18.480000000000018),
 'check_2': Checkbox(name='check_2', value=None, readonly=False, required=False, hidden=False, page_number=2, x=349.637, y=673.954, width=18.478999999999985, height=18.480000000000018),
 'check_3': Checkbox(name='check_3', value=None, readonly=False, required=False, hidden=False, page_number=3, x=349.305, y=667.344, width=18.480000000000018, height=18.479999999999905),
 'test': Text(name='test', value=None, readonly=False, required=False, hidden=False, page_number=1, x=73.3365, y=662.692, width=232.4235, height=21.067999999999984, comb=False, multiline=False),
 'test_2': Text(name='test_2', value=None, readonly=False, required=False, hidden=False, page_number=2, x=71.4095, y=671.626, width=232.42350000000005, height=21.067999999999984, comb=False, multiline=False),
 'test_3': Text(name='test_3', value=None, readonly=False, required=False, hidden=False, page_number=3, x=70.5919, y=665.349, width=232.42309999999998, height=21.067999999999984, comb=False, multiline=False)}
    ```

## Generate sample data

PyPDFForm can also generate sample data for filling a PDF form:

=== "Code"
    ```python
    from pprint import pprint
    from PyPDFForm import PdfWrapper

    pprint(PdfWrapper("sample_template.pdf").sample_data)
    ```
=== "Output"
    ```sh
    {'check': True,
    'check_2': True,
    'check_3': True,
    'test': 'test',
    'test_2': 'test_2',
    'test_3': 'test_3'}
    ```
