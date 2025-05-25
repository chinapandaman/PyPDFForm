# Fill PDF form

PyPDFForm fills a PDF form using a flat, non-nested dictionary.
The filled form is by default still editable. When you call the `fill` method, you can set the optional parameter `flatten` to `True` so that the filled form becomes flattened and uneditable.

## Fill text field and checkbox

When inspecting [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), note that text fields are filled with `string` values and checkboxes with `boolean` values.

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper(
    "sample_template.pdf",
    adobe_mode=False    # optional, set to True for Adobe Acrobat compatibility
).fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
    flatten=False   # optional, set to True to flatten the filled PDF form
)

filled.write("output.pdf")
```

## Fill radio button group

A radio button group is a collection of radio buttons sharing the same name on a PDF form.

A [PDF form](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_radio_button.pdf) 
with radio button groups can be filled using `integer` values where the value indicates which radio button to select 
among each radio button group:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper(
    "sample_template_with_radio_button.pdf",
    adobe_mode=False    # optional, set to True for Adobe Acrobat compatibility
).fill(
    {
        "radio_1": 0,
        "radio_2": 1,
        "radio_3": 2,
    },
    flatten=False   # optional, set to True to flatten the filled PDF form
)

filled.write("output.pdf")
```

## Fill dropdown

Like radio buttons, select a dropdown choice by specifying its `integer` value. For an example, see
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/dropdown/sample_template_with_dropdown.pdf).

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper(
    "sample_template_with_dropdown.pdf",
    adobe_mode=False    # optional, set to True for Adobe Acrobat compatibility
).fill(
    {
        "dropdown_1": 1
    },
    flatten=False   # optional, set to True to flatten the filled PDF form
)

filled.write("output.pdf")
```

## Fill signature

A signature field enables signing a PDF form with a handwritten signature image.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/signature/sample_template_with_signature.pdf) 
and [this signature image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_signature.png):

```python
from PyPDFForm import PdfWrapper

signed = PdfWrapper(
    "sample_template_with_signature.pdf",
    adobe_mode=False    # optional, set to True for Adobe Acrobat compatibility
).fill(
    {
        "signature": "sample_signature.png"
    },
    flatten=False   # optional, set to True to flatten the filled PDF form
)

filled.write("output.pdf")
```

**NOTE:** The signature value in your dictionary can be a file path, an open file object, or a `bytes` file stream, as described [here](install.md/#create-a-pdf-wrapper).

By default, the library preserves the aspect ratio of the signature image when filling it. This can be turned off by setting 
the `preserve_aspect_ratio` property to `False` on the signature field:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_signature.pdf")
pdf.widgets["signature"].preserve_aspect_ratio = False
pdf.fill(
    {
        "signature": "sample_signature.png"
    },
)

pdf.write("output.pdf")
```

## Fill image

Fill an image field similarly to a signature field, using a file path, file object, or file stream.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_image_field.pdf) 
and [this image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_image.jpg):

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper(
    "sample_template_with_image_field.pdf"
    adobe_mode=False    # optional, set to True for Adobe Acrobat compatibility
).fill(
    {
        "image_1": "sample_image.jpg"
    },
    flatten=False   # optional, set to True to flatten the filled PDF form
)

filled.write("output.pdf")
```

Unlike the signature field, the library does NOT preserve the aspect ratio of a regular image by default. It can be turned on by setting 
the `preserve_aspect_ratio` property to `True` on the image field:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_image_field.pdf")
pdf.widgets["image_1"].preserve_aspect_ratio = True
pdf.fill(
    {
        "image_1": "sample_image.jpg"
    },
)

pdf.write("output.pdf")
```
