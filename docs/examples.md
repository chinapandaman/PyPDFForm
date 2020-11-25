# Examples

This part of the documentation provides some useful example code snippets that 
can be used out of box.

## Preparing PDF Form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives that support the same functionalities.

For the purpose of consistency, all examples will use the same PDF form which can be 
found [here](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/sample_template.pdf). 
It has three text fields `test`, `test_2`, `test_3` and three checkboxes 
`check`, `check_2`, `check_3` scattered on three pages.

## Filling a PDF form

This example demos filling a PDF form in the most straight forward way 
and write it to an output disk file.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read()).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Fill a PDF form and enable editing

This example demos filling a PDF form but leave it editable after.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read()).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        editable=True,
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Set global font size and font color on filled text

This example sets a global font size of 20  and a global font color of red 
on the filled PDF form.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read(), simple_mode=False).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        font_size=20,
        font_color=(1, 0, 0),
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Wrap filled text with a length

Sometimes texts printed on the PDF form may be too lengthy. This example 
demos globally wrapping texts with a given length.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read(), simple_mode=False).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        text_wrap_length=2,
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Offset texts globally

This example offsets all texts printed on the PDF form by 100 horizontally 
and -100 vertically.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read(), simple_mode=False).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        text_x_offset=100,
        text_y_offset=-100,
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Draw image

This example demos how to draw an image on a PDF form.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

PATH_TO_IMAGE = os.path.join(
    os.path.expanduser("~"), "sample_image.jpeg"
)  # Change this to the location of an image of your choice

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    with open(PATH_TO_IMAGE, "rb+") as image:
        filled_pdf = PyPDFForm(template.read()).fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        ).draw_image(image.read(), 2, 100, 100, 400, 225, 0)

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Merge PDF forms

This example demos how to merge PDF together using the overloaded addition operator.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm()

    for i in range(3):
        filled_pdf = filled_pdf + PyPDFForm(template.read()).fill(
            {
                "test": "{}_test_1".format(i),
                "check": True,
                "test_2": "{}_test_2".format(i),
                "check_2": False,
                "test_3": "{}_test_3".format(i),
                "check_3": True,
            },
        )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

Alternatively you can use the assignment operator to achieve the same.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm()

    for i in range(3):
        filled_pdf += PyPDFForm(template.read()).fill(
            {
                "test": "{}_test_1".format(i),
                "check": True,
                "test_2": "{}_test_2".format(i),
                "check_2": False,
                "test_3": "{}_test_3".format(i),
                "check_3": True,
            },
        )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

## Fill with customized elements

A lot of times you may want one or more elements' details like font size and 
text wrap length to be different from the global setting. This can be done by manipulating 
the `elements` attributes of the object.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    pdf_form = PyPDFForm(template.read(), simple_mode=False)

    pdf_form.elements["test"].font_size = 20
    pdf_form.elements["test"].font_color = (1, 0, 0)
    pdf_form.elements["test_2"].text_x_offset = 50
    pdf_form.elements["test_2"].text_y_offset = -50
    pdf_form.elements["test_2"].text_wrap_length = 1
    pdf_form.elements["test_2"].font_color = (0, 1, 0)
    pdf_form.elements["test_3"].text_wrap_length = 2
    pdf_form.elements["test_3"].font_color = (0, 0, 1)

    pdf_form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(pdf_form.stream)
```
