# Draw elements

PyPDFForm enables you to draw elements on a PDF, which is useful when a field is missing from your PDF form or when you need to add text or images.

This section of the documentation uses [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

All optional parameters will have a comment `# optional` after each of them.

## Draw text

To use a custom font, see how to register it [here](font.md).

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf").draw_text(
    text="random text",
    page_number=1,
    x=300,
    y=225,
    font="your_registered_font",    # optional
    font_size=12,   # optional
    font_color=(1, 0, 0)    # optional
)

pdf.write("output.pdf")
```

## Draw image

For the rotation parameter, a positive value rotates the image counter-clockwise, and a negative value rotates it clockwise.

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf").draw_image(
    image="sample_image.jpg",
    page_number=1,
    x=100,
    y=100,
    width=400,
    height=225,
    rotation=0  # optional
)

pdf.write("output.pdf")
```
