# Fill a PDF form in place

The `FormWrapper` class allows you to fill a PDF form in place as if you were filling it manually.

## Normal mode

Similar to the `PdfWrapper` class, the `FormWrapper` also supports widgets including text fields, checkboxes, radio 
buttons, dropdowns, and paragraphs. However, it does NOT support signature or image widgets.

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

The optional parameter `flatten` has a default value of `False`, meaning PDF forms filled using `FormWrapper` will by 
default remain editable. Setting it to `True` will flatten the PDF after it's filled, making all widgets read only.

## Adobe mode (beta)

**NOTE:** This is a beta feature, meaning it still needs to be tested against more PDF forms and may not work for 
some of them.

Currently, there are some known issues with Adobe Acrobat displaying PDF forms filled using normal mode. 
Specifically the text content that gets filled into a text field widget will only appear when the text field is clicked 
and selected. This is not an issue in browsers like Chrome or other PDF viewing apps like Document Viewer 
(the default PDF app on Ubuntu).

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

**NOTE:** However, enabling Adobe mode may result in some unexpected style changes for checkboxes and radio buttons. It 
may even result in selected radio button not displaying correctly when opened using Adobe Acrobat. It's currently 
unclear why such behaviors exist. If you have trouble with these behaviors, consider using `PdfWrapper` instead to 
fill your PDF forms.
