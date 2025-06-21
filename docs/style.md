# Change form field styles

PyPDFForm enables you to modify some field styles through code, allowing you to change field appearances without altering the PDF form template.

This section of the documentation will primarily use [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Change text field font

Before changing a text field's font, you must first [register](font.md) the desired font.

After registration, you can apply the registered font to any text field:

```python
from PyPDFForm import PdfWrapper, Text

form = PdfWrapper("sample_template.pdf")

# change globally by iterating each text field
for field in form.widgets.values():
    if isinstance(field, Text):
        field.font = "your_registered_font"

# or change at each field's widget level
form.widgets["test"].font = "your_registered_font"

form.fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

form.write("output.pdf")
```

## Change text field font size

You can change the font size using a `float` value in PyPDFForm:

```python
from PyPDFForm import PdfWrapper, Text

form = PdfWrapper("sample_template.pdf")

# change globally by iterating each text field
for field in form.widgets.values():
    if isinstance(field, Text):
        field.font_size = 20

# or change at each field's widget level
form.widgets["test"].font_size = 30.5

form.fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

form.write("output.pdf")
```

## Change text field font color

You can change the font color using an RGB `tuple`:

```python
from PyPDFForm import PdfWrapper, Text

form = PdfWrapper("sample_template.pdf")

# change globally by iterating each text field
for field in form.widgets.values():
    if isinstance(field, Text):
        field.font_color = (1, 0, 0)

# or change at each field's widget level
form.widgets["test"].font_color = (0.2, 0, 0.5)

form.fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

form.write("output.pdf")
```

## Change checkbox/radio button size

You can change the size of a checkbox or a group of radio buttons using a `float` value:

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

form.write("output.pdf")
```

## Change dropdown field choices

You can change the choices of a dropdown field by setting a new list of strings. For example, the below snippet changes the dropdown field `dropdown_1` of [this PDF form](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf) to a new set of options:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template_with_dropdown.pdf")

form.widgets["dropdown_1"].choices = ["", "apple", "banana", "cherry", "dates"]

form.write("output.pdf")
```
