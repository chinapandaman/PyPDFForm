# Inspect form field data

After preparing a PDF form, use PyPDFForm to inspect its field names and determine the data required for filling it. You can choose from multiple inspection methods to suit your needs.

This section of the documentation uses [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Generate a JSON schema that describes a PDF form

You can describe the dictionary used to fill a PDF form using a JSON schema. For example:

```python
import json
from PyPDFForm import PdfWrapper

pdf_form_schema = PdfWrapper("sample_template.pdf").schema

print(json.dumps(pdf_form_schema, indent=4, sort_keys=True))
```

The above snippet will yield the following output:

```json
{
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

If your PDF form has already been filled, you can view its current filled data via the `.data` attribute. For example, below snippet inspects the current filled data for [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_filled.pdf):

```python
from pprint import pprint
from PyPDFForm import PdfWrapper

pprint(PdfWrapper("sample_template.pdf").data)
```

The above snippet will give you this dictionary:

```sh
{'check': True,
 'check_2': True,
 'check_3': True,
 'test': 'test',
 'test_2': 'test2',
 'test_3': 'test3'}
```

## Generate sample data

PyPDFForm can also generate sample data for filling a PDF form:

```python
from pprint import pprint
from PyPDFForm import PdfWrapper

pprint(PdfWrapper("sample_template.pdf").sample_data)
```

The above snippet will give you a sample dictionary:

```sh
{'check': True,
 'check_2': True,
 'check_3': True,
 'test': 'test',
 'test_2': 'test_2',
 'test_3': 'test_3'}
```
