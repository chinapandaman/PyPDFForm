# Change form field styles

PyPDFForm enables you to modify some field styles through code, allowing you to change field appearances without altering the PDF form template.

This section of the documentation will primarily use [this PDF](pdfs/sample_template.pdf) as an example.

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

## Change text field max length

You can change the maximum number of characters allowed in a text field:

```python
from PyPDFForm import PdfWrapper, Text

form = PdfWrapper("sample_template.pdf")

# change globally by iterating each text field
for field in form.widgets.values():
    if isinstance(field, Text):
        field.max_length = 4

# or change at each field's widget level
form.widgets["test"].max_length = 2

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

## Enable Text Field Character Spacing (Combs)

To enable character spacing in a text field, set its `.comb` property to `True`. This will evenly space out the characters of the text filled into the field. Note that this property only takes effect when the text field also has a `max_length` set.

```python
from PyPDFForm import PdfWrapper, Text

form = PdfWrapper("sample_template.pdf")

# change globally by iterating each text field
for field in form.widgets.values():
    if isinstance(field, Text):
        field.max_length = 4
        field.comb = True

# or change at each field's widget level
form.widgets["test"].max_length = 2
form.widgets["test"].comb = True

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

To modify the options available in a dropdown field, assign a new list of strings to the `.choices` attribute of the corresponding field. For instance, the following code snippet updates the `dropdown_1` field in [this PDF form](pdfs/sample_template_with_dropdown.pdf) with a new set of choices:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template_with_dropdown.pdf")

form.widgets["dropdown_1"].choices = ["", "apple", "banana", "cherry", "dates"]

form.write("output.pdf")
```

If you want different export values from the displayed options, you can specify a list of tuples for the `.choices` attribute, where the first value of each tuple is the displayed option and the second value is the export value:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template_with_dropdown.pdf")

form.widgets["dropdown_1"].choices = [
    ("", "blank_export_value"),
    ("apple", "apple_export_value"),
    ("banana", "banana_export_value"),
    ("cherry", "cherry_export_value"),
    ("dates", "dates_export_value"),
]

form.write("output.pdf")
```

## Change field editability

The `readonly` property of each form field controls its editability. Setting `readonly` to `True` flattens the field, making it uneditable, while setting it to `False` unflattens it, making it editable. For example, the following code snippet shows how you can make different form fields editable in [this PDF form](pdfs/sample_template_with_dropdown.pdf) after they have been flattened:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template_with_dropdown.pdf")

form.fill(
    {
        "test_1": "test_1",
        "test_2": "test_2",
        "test_3": "test_3",
        "check_1": True,
        "check_2": True,
        "check_3": True,
        "radio_1": 1,
        "dropdown_1": 0,
    },
    flatten=True,
)
form.widgets["test_2"].readonly = False  # text
form.widgets["check_3"].readonly = False  # checkbox
form.widgets["radio_1"].readonly = False  # radio button group
form.widgets["dropdown_1"].readonly = False  # dropdown

form.write("output.pdf")
```
