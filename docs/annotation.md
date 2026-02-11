# Annotate PDFs

PyPDFForm supports adding non-form-field annotations to PDFs.

This section uses [this PDF](pdfs/sample_template.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

Optional parameters are marked with an `# optional` comment.

## Create text annotations

Text annotations appear as sticky notes on a PDF. To create them, use the `PdfWrapper.annotate` method and pass a list of annotations:

```python
from PyPDFForm import Annotations, PdfWrapper

annotations = [
    Annotations.TextAnnotation(
        page_number=1,
        x=310,
        y=663,
        contents="this is an annotation",  # optional
        title="First Annotation",  # optional
    ),
    Annotations.TextAnnotation(
        page_number=2,
        x=310,
        y=672,
        contents="this is another annotation",  # optional
        title="Second Annotation",  # optional
        icon=Annotations.TextAnnotation.comment_icon,  # optional (1)
    ),
]

pdf = PdfWrapper("sample_template.pdf").annotate(annotations)

pdf.write("output.pdf")
```

1. Default is `note_icon`. Other options are `comment_icon`, `help_icon`, `key_icon`, and `insert_icon`.

## Create link annotations

???+ note
    At the moment, PyPDFForm only supports creating link annotations targeting URIs.

A link annotation navigates to a destination specified when clicked. The below snippet creates a link annotation on top of the text `TEST PDF TEMPLATE` that redirects to `https://www.google.com/`:

```python
from PyPDFForm import Annotations, PdfWrapper

pdf = PdfWrapper("sample_template.pdf").annotate(
    [
        Annotations.LinkAnnotation(
            page_number=1,
            x=70,
            y=705,
            width=95,
            height=20,
            uri="https://www.google.com/",
        )
    ]
)

pdf.write("output.pdf")
```

## Create text markup annotations

There are four types of text markup annotations: highlight, underline, squiggly, and strikeout. To create them, specify the coordinates and dimensions for the bounding box:

=== "Highlight"
    ```python
    from PyPDFForm import Annotations, PdfWrapper

    pdf = PdfWrapper("sample_template.pdf").annotate(
        [Annotations.HighlightAnnotation(page_number=1, x=70, y=705, width=95, height=20)]
    )

    pdf.write("output.pdf")
    ```
=== "Underline"
    ```python
    from PyPDFForm import Annotations, PdfWrapper

    pdf = PdfWrapper("sample_template.pdf").annotate(
        [Annotations.UnderlineAnnotation(page_number=1, x=70, y=705, width=95, height=20)]
    )

    pdf.write("output.pdf")
    ```
=== "Squiggly"
    ```python
    from PyPDFForm import Annotations, PdfWrapper

    pdf = PdfWrapper("sample_template.pdf").annotate(
        [Annotations.SquigglyAnnotation(page_number=1, x=70, y=705, width=95, height=20)]
    )

    pdf.write("output.pdf")
    ```
=== "Strikeout"
    ```python
    from PyPDFForm import Annotations, PdfWrapper

    pdf = PdfWrapper("sample_template.pdf").annotate(
        [Annotations.StrikeOutAnnotation(page_number=1, x=70, y=705, width=95, height=20)]
    )

    pdf.write("output.pdf")
    ```
