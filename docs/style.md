# Change text field styles

PyPDFForm gives you the ability to modify certain styles for text fields through code. This allows you to manipulate 
appearances of the texts without having to make changes to your PDF form template.

All these style changes can be done both globally upon instantiating a `PdfWrapper` object and individually for each 
text field widget.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Change font

Some fonts, for example `Courier` and `Helvetica`, are builtin as part of the PDF standards. These fonts can be set 
without registration:

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

Other non-standard fonts, for example [Liberation Serif](https://fonts.adobe.com/fonts/liberation-serif), will need 
a [TrueType file](https://github.com/chinapandaman/PyPDFForm/raw/master/font_samples/LiberationSerif-Regular.ttf) 
to be registered before they can be set:

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

PyPDFForm allows setting font size using a numerical `float` value:

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

PyPDFForm allows setting font color using an RGB numerical `tuple`:

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
