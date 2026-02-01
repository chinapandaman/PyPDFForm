# Annotate PDFs

PyPDFForm supports annotating PDFs by creating non-form-field annotations.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

All optional parameters will have a comment `# optional` after each of them.

## Create text annotations

Text annotations appear on a PDF in the form of sticky notes. To create them, use the `PdfWrapper.annotate` method and pass a list of annotations to create:

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
