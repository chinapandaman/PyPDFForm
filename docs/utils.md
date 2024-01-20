# Other utilities

There are some additional utilities PyPDFForm provides similar to many other PDF libraries.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Extract pages

Each `PdfWrapper` object has an attribute `.pages`. It's a `list` of `PdfWrapper` objects where each one of them is a 
single page:

```python
from PyPDFForm import PdfWrapper

first_page = PdfWrapper("sample_template.pdf").pages[0]
first_page.fill(
    {
        "test": "test_1",
        "check": True,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(first_page.read())
```

## Merge multiple PDFs

More than one PDF files can be merged by simply adding their `PdfWrapper` objects. Consider 
[this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf):

```python
from PyPDFForm import PdfWrapper

pdf_one = PdfWrapper("dummy.pdf")
pdf_two = PdfWrapper("sample_template.pdf")
merged = pdf_one + pdf_two

with open("output.pdf", "wb+") as output:
    output.write(merged.read())
```

Or if you wish to re-organize your pages:

```python
from PyPDFForm import PdfWrapper

pdf_one = PdfWrapper("dummy.pdf")
pdf_two = PdfWrapper("sample_template.pdf")
merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1] + pdf_two.pages[2]

with open("output.pdf", "wb+") as output:
    output.write(merged.read())
```

## Change PDF version

PyPDFForm supports modifying PDF version up to 2.0:

```python
from PyPDFForm import PdfWrapper

new_version = PdfWrapper("sample_template.pdf").change_version("2.0")

with open("output.pdf", "wb+") as output:
    output.write(new_version.read())
```
