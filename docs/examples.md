# Examples

This part of the documentation provides some useful example code snippets that 
can be used out of box.

## Preparing PDF Form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives that support the same functionalities.

For the purpose of consistency, all examples will use the same PDF form which can be 
found [here](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/sample_template.pdf). 
It has three text fields `test`, `test_2`, `test_3` and three checkboxes 
`check`, `check_2`, `check_3` scattered on three pages.

## Filling a PDF form

This example demos filling a PDF form in the most straight forward way 
and write it to an output disk file.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read()).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```
