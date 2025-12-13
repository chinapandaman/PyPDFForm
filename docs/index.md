# Welcome to PyPDFForm

PyPDFForm is a Python library for PDF form processing. It contains the essential functionalities needed to interact with PDF forms:

* Inspect what data a PDF form needs to be filled with.
* Fill a PDF form by simply creating a Python dictionary.
* Create form fields on a PDF.

It also supports other common utilities such as extracting pages and merging multiple PDFs together.

## Quickstart

Try some code snippets to get a flavor of how PyPDFForm works:

=== "Install"
    ```shell
    pip install PyPDFForm
    ```
=== "Instantiate"
    ```python
    from PyPDFForm import BlankPage, PdfWrapper

    pdf = PdfWrapper(BlankPage())
    ```
=== "Create"
    ```python
    from PyPDFForm import Fields, RawElements

    pdf.draw([
        RawElements.RawText("My Textfield:", 1, 100, 600),
        RawElements.RawText("My Checkbox:", 1, 100, 550),
    ])
    pdf.bulk_create_fields([
        Fields.TextField("my_textfield", 1, 180, 596, height=16),
        Fields.CheckBoxField("my_checkbox", 1, 180, 546, size=16),
    ])
    ```
=== "Inspect"
    ```python
    from pprint import pprint

    pprint(pdf.schema)
    ```
=== "Style"
    ```python
    pdf.widgets["my_textfield"].font_color = (1, 0, 0)
    pdf.widgets["my_textfield"].alignment = 1
    ```
=== "Fill"
    ```python
    pdf.fill({
        "my_textfield": "this is a text field",
        "my_checkbox": True,
    })
    ```
=== "Save"
    ```python
    pdf.write("output.pdf")
    ```

## What's next?

<div class="grid cards" markdown>

- :material-file-document-outline: [__User Guide__](install.md) for detailed usages
- :material-code-braces: [__Developer Guide__](dev_intro.md) if you wish to contribute to the project
- :fontawesome-solid-question: [__Open Issue__](https://github.com/chinapandaman/PyPDFForm/issues) for questions
- :fontawesome-regular-star: [__Star__](https://github.com/chinapandaman/PyPDFForm/stargazers) to support this project

</div>
