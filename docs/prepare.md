# Prepare a PDF form

The most common tool to create a PDF form is Adobe Acrobat. A tutorial can be found 
[here](https://helpx.adobe.com/acrobat/using/creating-distributing-pdf-forms.html). 
There are other free alternatives like [DocFly](https://www.docfly.com/) that support similar functionalities.

Given a PDF that's not a form yet, PyPDFForm also supports 
creating a subset of PDF form widgets on it through coding.

This section of the documentation will mostly use 
[this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) as an example.

This section of the documentation requires a basic understanding of [the PDF coordinate system](coordinate.md).

All optional parameters will have a comment `# optional` after each of them.

**NOTE:** For some PDF prep tools, creating widgets on their PDF forms may result in their original widgets getting 
flattened (e.g., [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_sejda.pdf) 
which was prepared using [Sejda](https://www.sejda.com/)). So it is advised that you fill them first 
before creating any widget using PyPDFForm.

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

## Modify the key of a widget

For existing widgets, PyPDFForm supports modifying their keys. 
Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), 
the below snippet will change the key of the first text field `test` to `test_text`:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("sample_template.pdf").update_widget_key(
    "test", "test_text"
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

If there is more than one widget with the same key, the optional parameter `index` can be used to pick which one 
to update. Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/scenario/issues/733.pdf), 
the below snippet will change the key of the second row's text field with the key `Description[0]` to `Description[1]`:

```python
from PyPDFForm import PdfWrapper

new_form = PdfWrapper("733.pdf").update_widget_key(
    "Description[0]", "Description[1]", index=1
)

with open("output.pdf", "wb+") as output:
    output.write(new_form.read())
```

Finally, if there are multiple widgets that need to be bulk updated, the performance optimal way of doing it is to set 
the optional parameter `defer` to `True` when updating each key and at the very end call `commit_widget_key_updates()` 
to commit all the updates.

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
