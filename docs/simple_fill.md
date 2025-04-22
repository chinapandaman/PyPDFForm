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

## Adobe mode (beta)

**NOTE:** This is a beta feature requiring further testing with various PDF forms and may not be compatible with all forms.

Adobe Acrobat has known issues displaying PDF forms filled in normal mode, where text content appears only when the text field is selected. This issue doesn't occur in browsers like Chrome or PDF viewers like Document Viewer (Ubuntu's default PDF app).

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

**NOTE:** Enabling Adobe mode may cause unexpected style changes to checkboxes and radio buttons, potentially affecting their display in Adobe Acrobat. If issues arise, consider using `PdfWrapper` to fill your PDF forms.
