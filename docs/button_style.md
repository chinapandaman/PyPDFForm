# Change checkbox and radio button styles

Similar to text fields discussed in the last chapter, PyPDFForm gives you the ability to 
modify some styles of checkboxes and radio buttons without changing the template.

## Change size

You can change the size of the selection by specifying a `float` value. Consider 
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

## Change button style

The button style is the shape of the selection on a checkbox or radio button. PyPDFForm lets you pick 
three different button styles: `check`, `circle`, and `cross`. Consider 
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
