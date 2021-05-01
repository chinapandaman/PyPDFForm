# Examples

This part of the documentation provides some useful example code snippets that 
can be used out of box.

## Preparing PDF Form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives like [sejda](https://www.sejda.com/) that support similar functionalities.

NOTE: Sejda is highly recommended as PyPDFForm 
provides more stable support to PDF forms prepared using it with a `sejda` mode.

Unless otherwise specified, all examples will use the same PDF form which can be 
found [here](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/v2/sample_template.pdf). 
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/simple_fill.py

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
            editable=True,
        )
        .read()
    )
```

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/simple_fill_editable.py

## Register font and set registered global font on filled text

This example registers a [LiberationSerif-Regular](https://github.com/chinapandaman/PyPDFForm/blob/master/font_samples/LiberationSerif-Regular.ttf) 
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
            PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM,
            simple_mode=False,
            global_font="LiberationSerif-Regular",
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_font.py

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
            simple_mode=False,
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_global_font_size_color.py

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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(
            PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM,
            simple_mode=False,
            global_text_wrap_length=2,
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_text_wrap.py

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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(
            PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM,
            simple_mode=False,
            global_text_x_offset=100,
            global_text_y_offset=-100,
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_text_offset.py

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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/draw_text.py

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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .draw_image(PATH_TO_IMAGE, 2, 100, 100, 400, 225, 0)
        .read()
    )
```

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/draw_image.py

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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/merge.py

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
    pdf_form = PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, simple_mode=False)

    pdf_form.elements["test"].font_size = 20
    pdf_form.elements["test"].font_color = (1, 0, 0)
    pdf_form.elements["test_2"].text_x_offset = 50
    pdf_form.elements["test_2"].text_y_offset = -50
    pdf_form.elements["test_2"].text_wrap_length = 1
    pdf_form.elements["test_2"].font_color = (0, 1, 0)
    pdf_form.elements["test_3"].font = "LiberationSerif-Italic"
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

    output.write(pdf_form.read())
```

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_customized_elements.py


## Fill a PDF form with radio buttons

This example uses this [template](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/v2/sample_template_with_radio_button.pdf). 
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

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/simple_fill_radio.py


## Fill a PDF form prepared using Sejda

This example uses this [template](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/v2/sample_template_sejda.pdf). 
It demos filling a PDF form prepared using Sejda.

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template_sejda.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, sejda=True)
        .fill(
            {
                "date": "01-01",
                "year": "21",
                "buyer_name": "John Doe",
                "buyer_address": "1 N Main St, Chicago, IL 60000",
                "seller_name": "Jack Smith",
                "seller_address": "2 S Main St, Chicago, IL 60000",
                "make": "AK",
                "model": "47",
                "caliber": "7.62-x39mm",
                "serial_number": "111111",
                "purchase_option": 0,
                "date_of_this_bill": True,
                "at_future_date": True,
                "other": True,
                "other_reason": "NO REASONS",
                "payment_amount": "400",
                "future_date": "01-01",
                "future_year": "22",
                "exchange_for": "Food",
                "buyer_name_printed": "John Doe",
                "seller_name_printed": "Jack Smith",
                "buyer_signed_date": "2021-01-01",
                "seller_signed_date": "2021-01-01",
                "buyer_dl_number": "D000-4609-0001",
                "seller_dl_number": "S530-4209-0001",
                "buyer_dl_state": "IL",
                "seller_dl_state": "IL",
            },
        )
        .read()
    )
```

Link to this example: https://github.com/chinapandaman/PyPDFForm/blob/master/examples/fill_sejda.py
