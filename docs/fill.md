# Fill a PDF form

PyPDFForm fills a PDF form using a flat, non-nested dictionary. The filled form is flattened and becomes non-editable to prevent encoding issues when combining multiple forms with overlapping widget names.

## Fill text field and checkbox widgets

When inspecting [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), note that text fields are filled with `string` values and checkboxes with `boolean` values.

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf").fill(
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
    output.write(filled.read())
```

## Fill radio button widgets

A radio button group is a collection of radio buttons sharing the same name on a PDF form.

A [PDF form](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_radio_button.pdf) 
with radio button groups can be filled using `integer` values where the value indicates which radio button to select 
among each radio button group:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template_with_radio_button.pdf").fill(
    {
        "radio_1": 0,
        "radio_2": 1,
        "radio_3": 2,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

## Fill dropdown widgets

Like radio buttons, select a dropdown choice by specifying its `integer` value. For an example, see
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf).

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template_with_dropdown.pdf").fill(
    {
        "dropdown_1": 1
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

## Fill signature widgets

A signature field widget enables signing a PDF form with a handwritten signature image.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/signature/sample_template_with_signature.pdf) 
and [this signature image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_signature.png):

```python
from PyPDFForm import PdfWrapper

signed = PdfWrapper("sample_template_with_signature.pdf").fill(
    {
        "signature": "sample_signature.png"
    },
)

with open("output.pdf", "wb+") as output:
    output.write(signed.read())
```

**NOTE:** The signature value in your dictionary can be a file path, an open file object, or a `bytes` file stream, as described [here](install.md/#create-a-pdf-wrapper).

By default, the library preserves the aspect ratio of the signature image when filling it. This can be turned off by setting 
the `preserve_aspect_ratio` property to `False` on the signature widget:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_signature.pdf")
pdf.widgets["signature"].preserve_aspect_ratio = False
pdf.fill(
    {
        "signature": "sample_signature.png"
    },
)

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```

## Fill image widgets

Fill an image field widget similarly to a signature field, using a file path, file object, or file stream.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_image_field.pdf) 
and [this image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_image.jpg):

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template_with_image_field.pdf").fill(
    {
        "image_1": "sample_image.jpg"
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

Unlike the signature field, the library does NOT preserve the aspect ratio of a regular image by default. It can be turned on by setting 
the `preserve_aspect_ratio` property to `True` on the image widget:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_image_field.pdf")
pdf.widgets["image_1"].preserve_aspect_ratio = True
pdf.fill(
    {
        "image_1": "sample_image.jpg"
    },
)

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```

## Disable rendering widgets

By default, PyPDFForm renders widgets on the filled PDF form despite flattening during the filling process. To disable this globally, pass `render_widgets=False` to the `PdfWrapper` object. For an example, see [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf).

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf", render_widgets=False).fill(
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
    output.write(filled.read())
```

To disable rendering for specific widgets, set the `render_widget` attribute to `False` at the individual widget level.

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")

pdf.widgets["check"].render_widget = False
pdf.widgets["check_2"].render_widget = False

pdf.fill(
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
    output.write(pdf.read())
```
