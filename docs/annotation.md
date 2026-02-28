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
    Currently, PyPDFForm only supports link annotations that target URIs.

A link annotation navigates to a specified destination when clicked. The following snippet creates a link annotation on top of the text `TEST PDF TEMPLATE` that redirects to `https://www.google.com/`:

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

## Create rubber stamp annotations

???+ note
    Currently Chromium based browsers have trouble rendering rubber stamp annotations correctly.

A rubber stamp annotation displays text or graphics intended to look as if they were stamped on the page with a rubber stamp. PyPDFForm supports a collection of predefined rubber stamps you can use to annotate PDFs:

```python
from PyPDFForm import Annotations, PdfWrapper

pdf = PdfWrapper("sample_template.pdf").annotate(
    [
        Annotations.RubberStampAnnotation(
            page_number=1,
            x=70,
            y=720,
            width=95,
            height=20,
            name=Annotations.RubberStampAnnotation.approved,  # optional (1)
        )
    ]
)

pdf.write("output.pdf")
```

1. Support `approved`, `experimental`, `not_approved`, `as_is`, `expired`, `not_for_public_release`, `confidential`, `final`, `sold`, `departmental`, `for_comment`, `top_secret`, `draft`, and `for_public_release`.
