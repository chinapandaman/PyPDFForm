# Inspect a PDF form

After preparing a PDF form, use PyPDFForm to inspect its widget names and determine the required filling data. You can choose from multiple inspection methods to suit your needs.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Generate a preview PDF

To inspect a PDF form, generate a preview document. The `PdfWrapper` object has a `.preview` attribute, which is a file stream that can be written to a file or memory buffer.

```python
from PyPDFForm import PdfWrapper

preview_stream = PdfWrapper("sample_template.pdf").preview

with open("output.pdf", "wb+") as output:
    output.write(preview_stream)
```

The generated preview PDF will have the name of each widget labeled on top of it in red.

## Generate a JSON schema that describes a PDF form

Describe the dictionary used to fill a PDF form using a JSON schema. For example:

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

Use the PyPDFForm-generated JSON schema to validate the data used for filling a PDF form.

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
