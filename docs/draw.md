# Draw elements

PyPDFForm enables you to draw elements on a PDF, which is useful when a field is missing from your PDF form or when you need to add text or images.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

All optional parameters will have a comment `# optional` after each of them.

## Draw text

When drawing multiple elements, it is more performant to create a list of those elements and draw them in a single operation.

```python
from PyPDFForm import PdfWrapper, RawElements

texts = [
    RawElements.RawText(
        text="random text",
        page_number=1,
        x=300,
        y=225,
        font="your_registered_font",  # optional (1)
        font_size=12,  # optional
        font_color=(1, 0, 0),  # optional
    ),
    RawElements.RawText(
        text="random text on page 2",
        page_number=2,
        x=300,
        y=225,
        font="your_registered_font",  # optional (2)
        font_size=12,  # optional
        font_color=(1, 0, 0),  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(texts)

pdf.write("output.pdf")
```

1.  To use a custom font, see how to register it [here](font.md).
2.  To use a custom font, see how to register it [here](font.md).

## Draw image

For the rotation parameter, a positive value rotates the image counter-clockwise, and a negative value rotates it clockwise.

```python
from PyPDFForm import PdfWrapper, RawElements

images = [
    RawElements.RawImage(
        image="sample_image.jpg",
        page_number=1,
        x=100,
        y=100,
        width=400,
        height=225,
        rotation=0,  # optional
    ),
    RawElements.RawImage(
        image="sample_image.jpg",
        page_number=2,
        x=100,
        y=100,
        width=400,
        height=225,
        rotation=180,  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(images)

pdf.write("output.pdf")
```
