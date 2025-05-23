# Prepare a PDF form

The most common tool for creating PDF forms is Adobe Acrobat, with a tutorial available
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html).
Alternative free tools like [DocFly](https://www.docfly.com/) offer similar functionality.

PyPDFForm also allows creating PDF form widgets on existing PDFs through coding.

This section of the documentation will mostly use 
[this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) as an example.

Understanding [the PDF coordinate system](coordinate.md) is necessary for this section.

All optional parameters will have a comment `# optional` after each of them.

## Create a text field widget

A text field widget can be created by downloading the PDF and running the following snippet:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="text",
    name="new_text_field_widget",
    page_number=1,
    x=57,
    y=700,
    width=120,  # optional
    height=40,  # optional
    max_length=5,   # optional
    comb=True,  # optional, when set to True, max_length must also be set
    font="Courier", # optional
    font_size=15,   # optional
    font_color=(1, 0, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5,  # optional
    alignment=0, # optional, 0=left, 1=center, 2=right
    multiline=True # optional
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Create a checkbox widget

A checkbox widget can be created using the same method with some changes to the parameters:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="checkbox",
    name="new_checkbox_widget",
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

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

The `button_style` parameter currently supports three options: `check`, `circle`, and `cross`.

## Create a radio button group

Unlike the other types of widgets, radio buttons must be created as a group. So for coordinate parameters `x` and `y`, you must specify a list of coordinates for each radio button under the group you are creating, and the length of the list must be more than one.

Other than that, radio button creation shares almost the same parameters as checkbox:

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

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Create a dropdown widget

A dropdown widget shares a similar set of parameters as a text field, with the only significant difference being
a list of `options` needs to be specified:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="dropdown",
    name="new_dropdown_widget",
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
    font="Courier", # optional
    font_size=15,   # optional
    font_color=(1, 0, 0),   # optional
    bg_color=(0, 0, 1, 1), # optional, (r, g, b, alpha)
    border_color=(1, 0, 0), # optional
    border_width=5  # optional
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Create a signature widget

A signature widget is only interactive in tools that support it. Otherwise, it will just be displayed as a rectangle, and clicking on it will not trigger any action.

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="signature",
    name="new_signature_widget",
    page_number=1,
    x=100,
    y=100,
    width=410,  # optional
    height=100,  # optional
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Create an image widget

Similar to a signature widget, an image widget is also only interactive in tools that support it.

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("dummy.pdf").create_widget(
    widget_type="image",
    name="new_image_widget",
    page_number=1,
    x=100,
    y=100,
    width=192,  # optional
    height=108,  # optional
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

## Modify the key of a widget

PyPDFForm allows modifying the keys of existing widgets.
For example, using [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf),
you can change the key of the first text field `test` to `test_text`:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("sample_template.pdf").update_widget_key(
    "test", "test_text"
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

If multiple widgets share the same key, use the `index` parameter to specify which one to update. For instance, with
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/scenario/issues/733.pdf),
you can change the key of the second row's text field with the key `Description[0]` to `Description[1]`:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("733.pdf").update_widget_key(
    "Description[0]", "Description[1]", index=1
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

For bulk updates, improve performance by setting `defer=True` when updating each key, then call `commit_widget_key_updates()` at the end to commit all changes.

Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/scenario/issues/733.pdf), 
the below snippet will change the key of each row's text field with the key `Description[0]` to `Description[i]` 
where `i` is the index of each row:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("733.pdf")

for i in range(1, 10):
    new_form.update_widget_key(
        "Description[0]", f"Description[{i}]", index=1, defer=True
    )

new_form.commit_widget_key_updates()

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```
