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

For the `rotation` parameter, a positive value rotates the image counter-clockwise, and a negative value rotates it clockwise.

=== "File Path"
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
=== "Open File Object"
    ```python
    from PyPDFForm import PdfWrapper, RawElements

    images = [
        RawElements.RawImage(
            image=open("sample_image.jpg", "rb+"),
            page_number=1,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=0,  # optional
        ),
        RawElements.RawImage(
            image=open("sample_image.jpg", "rb+"),
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
=== "Bytes File Stream"
    ```python
    from PyPDFForm import PdfWrapper, RawElements

    images = [
        RawElements.RawImage(
            image=open("sample_image.jpg", "rb+").read(),
            page_number=1,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=0,  # optional
        ),
        RawElements.RawImage(
            image=open("sample_image.jpg", "rb+").read(),
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

## Draw line

A line can be drawn by specifying starting and ending coordinates, and optionally its color.

```python
from PyPDFForm import PdfWrapper, RawElements

lines = [
    RawElements.RawLine(
        page_number=1,
        src_x=100,
        src_y=100,
        dest_x=100,
        dest_y=200,
    ),
    RawElements.RawLine(
        page_number=1,
        src_x=100,
        src_y=100,
        dest_x=200,
        dest_y=100,
        color=(0, 0, 1),  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(lines)

pdf.write("output.pdf")
```

## Draw rectangle

A rectangle can be drawn by specifying its coordinates and dimensions, and optionally its color and fill color.

```python
from PyPDFForm import PdfWrapper, RawElements

rectangles = [
    RawElements.RawRectangle(
        page_number=1,
        x=100,
        y=100,
        width=200,
        height=100,
    ),
    RawElements.RawRectangle(
        page_number=1,
        x=400,
        y=100,
        width=100,
        height=200,
        color=(0, 0, 1),  # optional
        fill_color=(0, 1, 0),  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(rectangles)

pdf.write("output.pdf")
```

## Draw circle

A circle can be drawn by specifying its center coordinates and radius, and optionally its color and fill color.

```python
from PyPDFForm import PdfWrapper, RawElements

circles = [
    RawElements.RawCircle(
        page_number=1,
        center_x=100,
        center_y=100,
        radius=50,
    ),
    RawElements.RawCircle(
        page_number=1,
        center_x=250,
        center_y=100,
        radius=100,
        color=(1, 0, 0),  # optional
        fill_color=(0, 1, 0),  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(circles)

pdf.write("output.pdf")
```

## Draw ellipse

An ellipse can be drawn by specifying its bounding box coordinates, and optionally its color and fill color.

```python
from PyPDFForm import PdfWrapper, RawElements

ellipses = [
    RawElements.RawEllipse(
        page_number=1,
        x1=100,
        y1=100,
        x2=250,
        y2=200,
    ),
    RawElements.RawEllipse(
        page_number=1,
        x1=300,
        y1=100,
        x2=500,
        y2=250,
        color=(1, 0, 0),  # optional
        fill_color=(0, 1, 0),  # optional
    ),
]

pdf = PdfWrapper("sample_template.pdf").draw(ellipses)

pdf.write("output.pdf")
```
