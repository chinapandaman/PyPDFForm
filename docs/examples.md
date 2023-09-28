# Examples

This part of the documentation provides some useful example code snippets that 
can be used out of box.

## Preparing PDF Form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives like [DocFly](https://www.docfly.com/) that support similar functionalities.

Unless otherwise specified, all examples will use the same PDF form which can be 
found [here](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf). 
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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )
        .read()
    )
```

## Register font and set registered global font on filled text

This example registers a [LiberationSerif-Regular](https://github.com/chinapandaman/PyPDFForm/raw/master/font_samples/LiberationSerif-Regular.ttf) 
font and sets it as the global font on the filled PDF form.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_SAMPLE_TTF_FONT_FILE = os.path.join(
    os.path.expanduser("~/Downloads"), "LiberationSerif-Regular.ttf"
)  # Change this to where you downloaded the sample font file

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

PyPDFForm.register_font("LiberationSerif-Regular", PATH_TO_SAMPLE_TTF_FONT_FILE)

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(
            PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, global_font="LiberationSerif-Regular",
        )
        .fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )
        .read()
    )
```

## Set global font size and font color on filled text

This example sets a global font size of 20, and a global font color of red 
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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(
            PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM,
            global_font_size=20,
            global_font_color=(1, 0, 0),
        )
        .fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )
        .read()
    )
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

PATH_TO_SAMPLE_TTF_FONT_FILE = os.path.join(
    os.path.expanduser("~/Downloads"), "LiberationSerif-Italic.ttf"
)  # Change this to where you downloaded the sample font file

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

PyPDFForm.register_font("LiberationSerif-Italic", PATH_TO_SAMPLE_TTF_FONT_FILE)

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    pdf_form = PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)

    pdf_form.elements["test"].font_size = 20
    pdf_form.elements["test"].font_color = (1, 0, 0)
    pdf_form.elements["test_2"].font_color = (0, 1, 0)
    pdf_form.elements["test_3"].font = "LiberationSerif-Italic"
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

    output.write(pdf_form.read())
```

## Fill a PDF form with radio buttons

This example uses this [template](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_radio_button.pdf). 
It demos filling a PDF form's radio button elements.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template_with_radio_button.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form


with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .fill({"radio_1": 0, "radio_2": 1, "radio_3": 2})
        .read()
    )
```

## Fill a PDF form with dropdown

This example uses this [template](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf). 
It demos filling a PDF form's dropdown elements.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template_with_dropdown.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form


with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .fill({"dropdown_1": 1})
        .read()
    )
```

## Draw text

Sometimes you may want to draw some texts on a PDF form 
even though there are no corresponding text elements. 
This example shows how.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .draw_text("drawn_text", 1, 300, 225)
        .read()
    )
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
    os.path.expanduser("~"), "sample_image.jpg"
)  # Change this to the location of an image of your choice

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .draw_image(PATH_TO_IMAGE, 2, 100, 100, 400, 225, 0)
        .read()
    )
```

## Merge PDF forms

This example demos how to merge PDFs together using the overloaded addition operator.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    filled_pdf = PyPDFForm()

    for i in range(3):
        filled_pdf += PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM).fill(
            {
                "test": "{}_test_1".format(i),
                "check": True,
                "test_2": "{}_test_2".format(i),
                "check_2": False,
                "test_3": "{}_test_3".format(i),
                "check_3": True,
            },
        )

    output.write(filled_pdf.read())
```

## Generate JSON schema

This example demos how to generate a JSON schema for a PDF form.

```python
import json
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

print(
    json.dumps(PyPDFForm(
        PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM
    ).generate_schema(), indent=4, sort_keys=True)
)
```

The above script will print the following JSON schema:

```json
{
    "properties": {
        "check": {
            "type": "boolean"
        },
        "check_2": {
            "type": "boolean"
        },
        "check_3": {
            "type": "boolean"
        },
        "test": {
            "type": "string"
        },
        "test_2": {
            "type": "string"
        },
        "test_3": {
            "type": "string"
        }
    },
    "type": "object"
}
```

## Changes the version of a PDF

This example demos how to change the version of a PDF to 2.0.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .change_version("2.0")
        .read()
    )
```
