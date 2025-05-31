# Create form fields

The most common tool for creating PDF form fields is Adobe Acrobat, and a tutorial is available [here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). Alternative free tools like [DocFly](https://www.docfly.com/) offer similar functionality.

PyPDFForm also allows creating PDF form fields on existing PDFs through coding.

This section of the documentation will primarily use [this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

All optional parameters will have a comment `# optional` after each of them.

## Create a text field

A text field can be created by downloading the PDF and running the following snippet:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="text",
    name="new_text_field",
    page_number=1,
    x=57,
    y=700,
    width=120,  # optional
    height=40,  # optional
    max_length=5,   # optional
    comb=True,  # optional, when set to True, max_length must also be set
    font="your_registered_font", # optional
    font_size=15,   # optional
    font_color=(1, 0, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5,  # optional
    alignment=0, # optional, 0=left, 1=center, 2=right
    multiline=True # optional
)

new_form.write("output.pdf")
```

To use a custom font, see how to register it [here](font.md).

## Create a checkbox

A checkbox can be created using the same method with some changes to the parameters:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="checkbox",
    name="new_checkbox",
    page_number=1,
    x=57,
    y=700,
    size=30,    # optional
    button_style="check",   # optional
    tick_color=(0, 1, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5  # optional
)

new_form.write("output.pdf")
```

The `button_style` parameter currently supports three options: `check`, `circle`, and `cross`.

## Create a radio button group

Unlike other field types, radio buttons must be created as a group. Therefore, for the coordinate parameters `x` and `y`, you must specify a list of coordinates for each radio button within the group, and the list must contain more than one coordinate.

Otherwise, radio button creation shares almost the same parameters as a checkbox:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="radio",
    name="new_radio_group",
    page_number=1,
    x=[50, 100, 150],
    y=[50, 100, 150],
    size=30,    # optional
    button_style="check",   # optional
    shape="square", # optional, circle or square
    tick_color=(0, 1, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5  # optional
)

new_form.write("output.pdf")
```

## Create a dropdown field

A dropdown field shares a similar set of parameters as a text field. The only significant difference is that a list of `options` needs to be specified:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="dropdown",
    name="new_dropdown",
    page_number=1,
    x=57,
    y=700,
    options=[
        "foo",
        "bar",
        "foobar",
    ],
    width=120,  # optional
    height=40,  # optional
    font="your_registered_font", # optional
    font_size=15,   # optional
    font_color=(1, 0, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5  # optional
)

new_form.write("output.pdf")
```

To use a custom font, see how to register it [here](font.md).

## Create a signature field

A signature field is only interactive in tools that support it. Otherwise, it is displayed as a rectangle, and clicking it will not trigger any action:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="signature",
    name="new_signature",
    page_number=1,
    x=100,
    y=100,
    width=410,  # optional
    height=100,  # optional
)

new_form.write("output.pdf")
```

## Create an image field

Similar to a signature field, an image field is also only interactive in tools that support it:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="image",
    name="new_image",
    page_number=1,
    x=100,
    y=100,
    width=192,  # optional
    height=108,  # optional
)

new_form.write("output.pdf")
```

## Modify the key of a field

PyPDFForm allows you to modify the keys of existing fields. For example, to change the key of the first text field, `test`, to `test_text` using [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), use the following code:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("sample_template.pdf").update_widget_key(
    "test", "test_text"
)

new_form.write("output.pdf")
```

If multiple fields share the same key, use the `index` parameter to specify which one to update. For instance, to change the key of the second row's text field with the key `Description[0]` to `Description[1]` using [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/scenario/issues/733.pdf), use the following code:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("733.pdf").update_widget_key(
    "Description[0]", "Description[1]", index=1
)

new_form.write("output.pdf")
```

For bulk updates, improve performance by setting `defer=True` when updating each key, then call `commit_widget_key_updates()` at the end to commit all changes.

To change the key of each row's text field with the key `Description[0]` to `Description[i]`, where `i` is the index of each row, using [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/scenario/issues/733.pdf), use the following code:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("733.pdf")

for i in range(1, 10):
    new_form.update_widget_key(
        "Description[0]", f"Description[{i}]", index=1, defer=True
    )

new_form.commit_widget_key_updates().write("output.pdf")
```
