# Fill a PDF form in place

The `FormWrapper` class enables filling a PDF form in place, simulating manual filling.

## Normal mode

Like `PdfWrapper`, `FormWrapper` supports widgets such as text fields, checkboxes, radio buttons, dropdowns, and paragraphs, but not signature or image widgets.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf):

```python
from PyPDFForm import FormWrapper

filled = FormWrapper("sample_template_with_dropdown.pdf").fill(
    {
        "test_1": "test_1",
        "test_2": "test_2",
        "test_3": "test_3",
        "check_1": True,
        "check_2": True,
        "check_3": True,
        "radio_1": 1,
        "dropdown_1": 1,
    },
    flatten=False,  # optional
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

The `flatten` parameter defaults to `False`, keeping PDF forms filled with `FormWrapper` editable. Set it to `True` to flatten the PDF and make widgets read-only.

## Adobe mode

Adobe Acrobat has known issues displaying PDF forms filled in normal mode. Specifically, text content may only be visible when the text field is selected. This issue is not present in browsers like Chrome or PDF viewers such as Document Viewer (Ubuntu's default PDF application).

By setting the optional parameter `adobe_mode` (default value is `False`) to `True` when invoking the `fill` 
method, `FormWrapper` will fill a PDF form such that its text 
fields will be displayed correctly when opened using Adobe Acrobat. Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf):

```python
from PyPDFForm import FormWrapper

filled = FormWrapper("sample_template_with_dropdown.pdf").fill(
    {
        "test_1": "test_1",
        "test_2": "test_2",
        "test_3": "test_3",
        "check_1": True,
        "check_2": True,
        "check_3": True,
        "radio_1": 1,
        "dropdown_1": 1,
    },
    adobe_mode=True, # optional
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

**NOTE:** PDF forms filled with `adobe_mode` enabled are optimized for viewing in Adobe Acrobat. Other PDF viewers may experience rendering issues with certain widget styles, such as text font or widget borders.
So only enable `adobe_mode` when the generated PDFs are meant to be viewed by Adobe Acrobat.
