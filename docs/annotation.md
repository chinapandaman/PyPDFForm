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
