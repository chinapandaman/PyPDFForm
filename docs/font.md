# Register fonts

PyPDFForm allows you to use customized fonts in some APIs. To do so, you first need to register the TrueType file of the font you want to use.

For example, if you want to use one of the [Liberation Serif](https://fonts.adobe.com/fonts/liberation-serif) font family, you can register its [TrueType file](https://github.com/chinapandaman/PyPDFForm/raw/master/font_samples/LiberationSerif-BoldItalic.ttf) as follows:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf")
form.register_font("new_font_name", "LiberationSerif-BoldItalic.ttf")
```

In this case the font `LiberationSerif-BoldItalic` is registered under the name `new_font_name`. From now on you can reference this font in APIs of this object using the name `new_font_name`.
