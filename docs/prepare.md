# Prepare a PDF form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives like [DocFly](https://www.docfly.com/) that support similar functionalities.

Given a PDF that's not a form yet, PyPDFForm also supports 
creating a subset of PDF form widgets on it through coding.

This section of the documentation will use 
[this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) as an example.

This section of the documentation requires a basic understanding of [the PDF coordinate system](coordinate.md).

**NOTE:** For some PDF prep tools, creating widgets on their PDF forms may result in their original widgets getting 
flattened (e.g., [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_sejda.pdf) 
which was prepared using [Sejda](https://www.sejda.com/)). So it is advised that you fill them first 
before creating any widget using PyPDFForm.

## Create a text field widget

A text field widget can be created by downloading the PDF and running the following snippet:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="text",
    name="new_text_field_widget",
    page_number=1,
    x=57,
    y=700,
    width=120,
    height=40,
    max_length=5,
    font="Courier",
    font_size=15,
    font_color=(1, 0, 0)
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Create a checkbox widget

A checkbox widget can be created using the same method with some changes to the parameters:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="checkbox",
    name="new_checkbox_widget",
    page_number=1,
    x=57,
    y=700,
    size=30,
    button_style="check"
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

The `button_style` parameter currently supports three options: `check`, `circle`, and `cross`.

## Create a dropdown widget

A dropdown widget shares a similar set of parameters as a text field, with the only significant difference being
a list of `options` needs to be specified:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="dropdown",
    name="new_dropdown_widget",
    page_number=1,
    x=57,
    y=700,
    options=[
        "foo",
        "bar",
        "foobar",
    ],
    width=120,
    height=40,
    font="Courier",
    font_size=15,
    font_color=(1, 0, 0)
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```
