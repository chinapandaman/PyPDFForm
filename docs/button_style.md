# Change checkbox and radio button styles

PyPDFForm allows you to modify certain styles of checkboxes and radio buttons without altering the template, similar to text fields.

## Change size

To change the size of the selection, specify a `float` value. For an example, refer to
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf):

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf")
form.widgets["check"].size = 50
form.widgets["check_2"].size = 40
form.widgets["check_3"].size = 60

form.fill(
    {
        "check": True,
        "check_2": True,
        "check_3": True,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```

<!-- TODO: no longer supported -->
## Change button style

The button style determines the shape of the selection on a checkbox or radio button. PyPDFForm offers
three button styles: `check`, `circle`, and `cross`. For an example, see
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_radio_button.pdf):

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template_with_radio_button.pdf")
form.widgets["radio_1"].button_style = "cross"
form.widgets["radio_2"].button_style = "circle"
form.widgets["radio_3"].button_style = "check"

form.fill(
    {
        "radio_1": 0,
        "radio_2": 1,
        "radio_3": 2,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```
