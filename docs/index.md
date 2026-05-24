# Welcome to PyPDFForm

PyPDFForm is a Python library for PDF form processing. It contains the essential functionalities needed to interact with PDF forms:

* Inspect what data a PDF form needs to be filled with.
* Fill a PDF form by simply creating a Python dictionary.
* Create form fields on a PDF.

It also supports other common utilities such as extracting pages and merging multiple PDFs together.

## Quickstart

Here's a quick look at how PyPDFForm works:

=== "Python Library"
    ```python
    from pprint import pprint
    from PyPDFForm import BlankPage, Fields, PdfWrapper, RawElements

    # Create a blank PDF
    pdf = PdfWrapper(BlankPage())

    # Draw labeling texts
    pdf.draw(
        [
            RawElements.RawText("My Textfield:", 1, 100, 600),
            RawElements.RawText("My Checkbox:", 1, 100, 550),
        ]
    )

    # Create text and checkbox fields
    pdf.bulk_create_fields(
        [
            Fields.TextField("my_textfield", 1, 180, 596, height=16),
            Fields.CheckBoxField("my_checkbox", 1, 180, 546, size=16),
        ]
    )

    # Inspect the fields via JSON schema
    pprint(pdf.schema)

    # Change the field styles
    pdf.widgets["my_textfield"].font_color = (1, 0, 0)
    pdf.widgets["my_textfield"].alignment = 1

    # Fill the newly created form
    pdf.fill(
        {
            "my_textfield": "this is a text field",
            "my_checkbox": True,
        }
    )

    # Save the new form
    pdf.write("output.pdf")
    ```

## What's next?

<div class="grid cards" markdown>

- :material-file-document-outline: Read the [__User Guide__](install.md) for detailed usage guides.
- :material-code-braces: Read the [__Developer Guide__](dev_intro.md) if you want to contribute.
- :fontawesome-solid-bug: Submit [__GitHub Issues__](https://github.com/chinapandaman/PyPDFForm/issues) to report bugs.
- :fontawesome-regular-star: [__Star__](https://github.com/chinapandaman/PyPDFForm/stargazers) to support this project.

</div>
