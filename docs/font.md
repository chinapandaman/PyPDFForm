# Register fonts

PyPDFForm enables the use of custom fonts in certain APIs. To use a custom font, you must first register its TrueType (.ttf) file.

For example, to use a font from the [Liberation Serif](https://fonts.adobe.com/fonts/liberation-serif) family, register its TrueType file (e.g., [LiberationSerif-BoldItalic.ttf](https://github.com/chinapandaman/PyPDFForm/blob/master/font_samples/LiberationSerif-BoldItalic.ttf)) as follows:

=== "File Path"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    form.register_font("new_font_name", "LiberationSerif-BoldItalic.ttf")
    ```
=== "Open File Object"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    with open("LiberationSerif-BoldItalic.ttf", "rb+") as font_file:
        form.register_font("new_font_name", font_file)
    ```
=== "Bytes File Stream"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    with open("LiberationSerif-BoldItalic.ttf", "rb+") as font_file:
        form.register_font("new_font_name", font_file.read())
    ```

In this example, `LiberationSerif-BoldItalic.ttf` is registered as `new_font_name`. You can now reference this font in the object's APIs using the name `new_font_name`.

## Get registered fonts

To see which fonts have been registered, access the `fonts` attribute of the `PdfWrapper` object:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf")
form.register_font("new_font_name", "LiberationSerif-BoldItalic.ttf")

print(form.fonts)
```

The `fonts` attribute lists the names of the registered fonts.
