# Annotate PDFs

PyPDFForm supports adding non-form-field annotations to PDFs.

This section uses [this PDF](pdfs/sample_template.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

In the library examples, optional parameters are marked with an `# optional` comment.

## Create text annotations

Text annotations appear as sticky notes on a PDF.

=== "Library"
    Use the `PdfWrapper.annotate` method and pass a list of annotations:

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

    1. The default icon is `note_icon`. Other options are `comment_icon`, `help_icon`, `key_icon`, and `insert_icon`.
=== "CLI"
    Use the `create annotation` command with a JSON file that contains a `text` array:

    === "data.json"
        ```json
        {
            "text": [
                {
                    "page_number": 1,
                    "x": 310,
                    "y": 663,
                    "contents": "this is an annotation",
                    "title": "First Annotation"
                },
                {
                    "page_number": 2,
                    "x": 310,
                    "y": 672,
                    "contents": "this is another annotation",
                    "title": "Second Annotation",
                    "icon": "/Comment"
                }
            ]
        }
        ```
    === "Command"
        ```shell
        pypdfform create annotation sample_template.pdf -f data.json -o output.pdf
        ```

## Create link annotations

A link annotation opens a destination when clicked. The destination can be a URI or another page in the same PDF.

=== "Library"
    === "URI"
        The following snippet creates a link annotation over the text `TEST PDF TEMPLATE` that opens `https://www.google.com/`:

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
    === "Another Page"
        The following snippet creates a link annotation over the text `TEST PDF TEMPLATE` that jumps to the second page of the PDF:

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
                    page=2,
                )
            ]
        )

        pdf.write("output.pdf")
        ```
=== "CLI"
    Use the `create annotation` command with a JSON file that contains a `link` array. Each link must include exactly one of `uri` or `page`. The command example uses `uri.json`; replace it with `page.json` to create a link to another page.

    === "uri.json"
        ```json
        {
            "link": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20,
                    "uri": "https://www.google.com/"
                }
            ]
        }
        ```
    === "page.json"
        ```json
        {
            "link": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20,
                    "page": 2
                }
            ]
        }
        ```
    === "Command"
        ```shell
        pypdfform create annotation sample_template.pdf -f uri.json -o output.pdf
        ```

## Create text markup annotations

There are four types of text markup annotations: highlight, underline, squiggly, and strikeout. To create them, specify the coordinates and dimensions for the bounding box:

=== "Library"
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
=== "CLI"
    Use the `create annotation` command with a JSON file whose top-level key matches the markup type. The command example uses `highlight.json`; replace it with the file for the markup type you want.

    === "highlight.json"
        ```json
        {
            "highlight": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20
                }
            ]
        }
        ```
    === "underline.json"
        ```json
        {
            "underline": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20
                }
            ]
        }
        ```
    === "squiggly.json"
        ```json
        {
            "squiggly": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20
                }
            ]
        }
        ```
    === "strikeout.json"
        ```json
        {
            "strikeout": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 705,
                    "width": 95,
                    "height": 20
                }
            ]
        }
        ```
    === "Command"
        ```shell
        pypdfform create annotation sample_template.pdf -f highlight.json -o output.pdf
        ```

## Create rubber stamp annotations

???+ note
    Currently, Chromium-based browsers have trouble rendering rubber stamp annotations correctly.

A rubber stamp annotation places stamp text or graphics on the page. PyPDFForm supports a collection of predefined rubber stamps you can use to annotate PDFs:

=== "Library"
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

    1. Supported stamp names are `approved`, `experimental`, `not_approved`, `as_is`, `expired`, `not_for_public_release`, `confidential`, `final`, `sold`, `departmental`, `for_comment`, `top_secret`, `draft`, and `for_public_release`.
=== "CLI"
    Use the `create annotation` command with a JSON file that contains a `stamp` array:

    === "data.json"
        ```json
        {
            "stamp": [
                {
                    "page_number": 1,
                    "x": 70,
                    "y": 720,
                    "width": 95,
                    "height": 20,
                    "name": "/Approved"
                }
            ]
        }
        ```
    === "Command"
        ```shell
        pypdfform create annotation sample_template.pdf -f data.json -o output.pdf
        ```
