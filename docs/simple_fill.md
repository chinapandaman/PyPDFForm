# Fill a PDF form in place

The `FormWrapper` class allows you to fill a PDF form in place as if you were filling it manually.

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
