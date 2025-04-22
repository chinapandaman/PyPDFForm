# Change text field styles

PyPDFForm enables modifying text field styles through code, allowing you to change text appearances without altering the PDF form template.

You can apply these style changes globally when creating a `PdfWrapper` object or individually for each text field widget.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Change font

Some fonts like `Courier` and `Helvetica` are built into PDF standards and can be set without registration:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf", global_font="Courier")
form.widgets["test"].font = "Helvetica"

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

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```

To use non-standard fonts like [Liberation Serif](https://fonts.adobe.com/fonts/liberation-serif), register a
[TrueType file](https://github.com/chinapandaman/PyPDFForm/raw/master/font_samples/LiberationSerif-Regular.ttf) before setting the font:

```python
from PyPDFForm import PdfWrapper

PdfWrapper.register_font("new_font_name", "LiberationSerif-Regular.ttf")

form = PdfWrapper("sample_template.pdf", global_font="new_font_name")
form.widgets["test"].font = "new_font_name"

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

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```

## Change font size

Set font size using a `float` value in PyPDFForm:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf", global_font_size=20)
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

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```

## Change font color

In PyPDFForm, set font color using an RGB `tuple`:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf", global_font_color=(1, 0, 0))
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

with open("output.pdf", "wb+") as output:
    output.write(form.read())
```
