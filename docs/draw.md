# Draw stuffs

PyPDFForm allows you to draw certain elements on a PDF. The purpose is in case there is a missing widget on your PDF 
form, and you need to put certain texts on it, or if you need to draw images.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Draw text

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf").draw_text(
    text="random text",
    page_number=1,
    x=300,
    y=225
)

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```

## Draw image

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf").draw_image(
    image="sample_image.jpg",
    page_number=1,
    x=100,
    y=100,
    width=400,
    height=225,
    rotation=0
)

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```
