# Fill a PDF form

PyPDFForm uses a single depth, non-nested dictionary to fill a PDF form. As a result of this process, the filled 
PDF form will be flattened and no longer editable. This is to prevent future encoding issues, especially when 
multiple PDF forms with overlaps on widget names are combined together.

## Fill text field and checkbox widgets

As seen when we 
inspected [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), a text 
field can be filled with a value of `string`, whereas a checkbox can be filled with a `boolean` value:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf").fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

## Fill radio button widgets

A radio button group on a PDF form is a collection of radio buttons that share the same name.

A [PDF form](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_radio_button.pdf) 
with radio button groups can be filled using `integer` values where the value indicates which radio button to select 
among each radio button group:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template_with_radio_button.pdf").fill(
    {
        "radio_1": 0,
        "radio_2": 1,
        "radio_3": 2,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

## Fill dropdown widgets

Similar to radio buttons, a dropdown choice can be selected by specifying an `integer` value of the choice. Consider 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf):

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template_with_dropdown.pdf").fill(
    {
        "dropdown_1": 1
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```
