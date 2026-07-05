# Welcome to PyPDFForm

PyPDFForm is a Python library and command line tool for working with PDF forms. It provides Python APIs and CLI commands for creating, inspecting, updating, and filling forms, plus common PDF utilities.

With PyPDFForm, you can:

* Create PDF forms, form fields, and raw elements.
* Inspect form fields, metadata, and values.
* Update field styling, behavior, and scripts.
* Fill PDF forms.
* Extract pages and merge PDFs.

The goal is to make PDF form work straightforward, whether you are handling one document or building a larger workflow.

## Quickstart

=== "Library"
    Here's a quick look at PyPDFForm as a Python library:

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

=== "CLI"
    The same workflow can be run from the CLI:

    === "Commands"
        ```shell
        pypdfform create blank -o output.pdf
        pypdfform create raw output.pdf -f labels.yaml
        pypdfform create field output.pdf -f fields.yaml
        pypdfform inspect schema output.pdf
        pypdfform update field output.pdf -f styles.yaml
        pypdfform fill output.pdf -f data.yaml
        ```
    === "labels.yaml"
        ```yaml
        text:
          - text: 'My Textfield:'
            page_number: 1
            x: 100
            y: 600
          - text: 'My Checkbox:'
            page_number: 1
            x: 100
            y: 550
        ```
    === "fields.yaml"
        ```yaml
        text:
          - name: my_textfield
            page_number: 1
            x: 180
            y: 596
            height: 16
        check:
          - name: my_checkbox
            page_number: 1
            x: 180
            y: 546
            size: 16
        ```
    === "styles.yaml"
        ```yaml
        my_textfield:
          font_color:
            - 1
            - 0
            - 0
          alignment: 1
        ```
    === "data.yaml"
        ```yaml
        my_textfield: this is a text field
        my_checkbox: true
        ```

## What's next?

<div class="grid cards" markdown>

- :material-file-document-outline: Read the [__User Guide__](install.md) for detailed usage guides.
- :material-code-braces: Read the [__Developer Guide__](dev_intro.md) if you want to contribute.
- :fontawesome-solid-bug: Submit [__GitHub Issues__](https://github.com/chinapandaman/PyPDFForm/issues) to report bugs.
- :fontawesome-regular-star: [__Star__](https://github.com/chinapandaman/PyPDFForm/stargazers) to support this project.

</div>
