# Fill a PDF form

PyPDFForm uses a single depth, non-nested dictionary to fill a PDF form. As a result of this process, the filled 
PDF form will be flattened and no longer editable. This is to prevent future encoding issues, especially when 
multiple PDF forms with overlaps on widget names are combined.

## Fill text field and checkbox widgets

As seen when we 
inspected [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), a text 
field can be filled with a value of `string`, whereas a checkbox can be filled with a `boolean` value:

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

A radio button group on a PDF form is a collection of radio buttons that share the same name.

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

Similar to radio buttons, a dropdown choice can be selected by specifying an `integer` value of the choice. Consider 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf):

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

A signature field widget allows you to sign a PDF form in a handwritten format. PyPDFForm lets you use a signature image to populate 
any signature field widget.

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

**NOTE:** As described [here](install.md/#create-a-pdf-wrapper), the value of the signature in your dictionary can be 
a file path shown above, but also an open file object and a file stream that's in `bytes`.

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

An image field widget can be filled similarly to a signature field, by providing a value of file path, file object, or 
file stream.

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
