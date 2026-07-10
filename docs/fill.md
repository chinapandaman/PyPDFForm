# Fill PDF forms

PyPDFForm fills PDF forms from a mapping of field names to values. In the library, that mapping is a Python dictionary; in the CLI, it can be a YAML or JSON file or a set of dynamic field options.

Most fields use flat, non-nested values. Image and signature fields can also use nested CLI objects when you need per-field options such as `preserve_aspect_ratio`.

Filled forms stay editable by default. Pass `flatten=True` to `fill`, or add `--flatten` to the CLI command, to flatten fields after filling so their values can no longer be edited.

## Fill from a data file or CLI options (CLI only)

The CLI accepts form data from a YAML or JSON file passed with `--file` / `-f`:

=== "data.yaml"
    ```yaml
    test: test_1
    check: true
    test_2: test_2
    check_2: false
    test_3: test_3
    check_3: true
    ```
=== "Command"
    ```shell
    pypdfform fill sample_template.pdf -f data.yaml -o output.pdf
    ```

You can pass the same mapping directly as dynamic options, using each field name as an option name:

```shell
pypdfform fill sample_template.pdf \
    --test test_1 \
    --check true \
    --test_2 test_2 \
    --check_2 false \
    --test_3 test_3 \
    --check_3 true \
    -o output.pdf
```

If `--file` and dynamic options are both present, the file data takes precedence.

## Fill text field and checkbox

Use string values for text fields and boolean values for checkboxes. The following example fills [this PDF](pdfs/sample_template.pdf):

=== "Library"
    ```python
    from PyPDFForm import PdfWrapper

    filled = PdfWrapper("sample_template.pdf").fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        flatten=False   # optional, set to True to flatten the filled PDF form
    )

    filled.write("output.pdf")
    ```
=== "CLI"
    === "data.yaml"
        ```yaml
        test: test_1
        check: true
        test_2: test_2
        check_2: false
        test_3: test_3
        check_3: true
        ```
    === "Command"
        ```shell
        pypdfform fill sample_template.pdf -f data.yaml -o output.pdf
        ```

## Fill radio button group

A radio button group is a collection of radio buttons sharing the same name on a PDF form.

Fill each radio button group with the zero-based index of the option to select. For example, to fill [this PDF](pdfs/sample_template_with_radio_button.pdf):

=== "Library"
    ```python
    from PyPDFForm import PdfWrapper

    filled = PdfWrapper("sample_template_with_radio_button.pdf").fill(
        {
            "radio_1": 0,
            "radio_2": 1,
            "radio_3": 2,
        },
        flatten=False   # optional, set to True to flatten the filled PDF form
    )

    filled.write("output.pdf")
    ```
=== "CLI"
    === "data.yaml"
        ```yaml
        radio_1: 0
        radio_2: 1
        radio_3: 2
        ```
    === "Command"
        ```shell
        pypdfform fill sample_template_with_radio_button.pdf -f data.yaml -o output.pdf
        ```

## Fill dropdown field

A dropdown can be filled with either the zero-based option index or the option text. For example, to fill [this PDF](pdfs/sample_template_with_dropdown.pdf):

=== "Library"
    === "Using Option Index"
        ```python
        from PyPDFForm import PdfWrapper

        filled = PdfWrapper("sample_template_with_dropdown.pdf").fill(
            {
                "dropdown_1": 1
            },
            flatten=False   # optional, set to True to flatten the filled PDF form
        )

        filled.write("output.pdf")
        ```
    === "Using String Value"
        You can also specify a dropdown option by its `string` value:

        ```python
        from PyPDFForm import PdfWrapper

        filled = PdfWrapper("sample_template_with_dropdown.pdf").fill(
            {
                "dropdown_1": "bar"
            },
            flatten=False   # optional, set to True to flatten the filled PDF form
        )

        filled.write("output.pdf")
        ```
=== "CLI"
    === "data.yaml"
        ```yaml
        dropdown_1: 1
        ```
    === "string_value.yaml"
        ```yaml
        dropdown_1: bar
        ```
    === "Command"
        ```shell
        pypdfform fill sample_template_with_dropdown.pdf -f data.yaml -o output.pdf
        ```

???+ note
    If you fill a dropdown field with a `string` value that is not one of its existing options, the new value is added as the last option in the dropdown and automatically selected.

## Fill signature field

A signature field can be filled with a handwritten signature image.

The examples below use [this PDF](pdfs/sample_template_with_signature.pdf) and [this signature image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_signature.png):

=== "Library"
    === "File Path"
        ```python
        from PyPDFForm import PdfWrapper

        signed = PdfWrapper("sample_template_with_signature.pdf").fill(
            {
                "signature": "sample_signature.png"
            },
            flatten=False   # optional, set to True to flatten the filled PDF form
        )

        signed.write("output.pdf")
        ```
    === "Open File Object"
        ```python
        from PyPDFForm import PdfWrapper

        with open("sample_signature.png", "rb+") as sig:
            signed = PdfWrapper("sample_template_with_signature.pdf").fill(
                {
                    "signature": sig
                },
                flatten=False   # optional, set to True to flatten the filled PDF form
            )

        signed.write("output.pdf")
        ```
    === "Bytes File Stream"
        ```python
        from PyPDFForm import PdfWrapper

        with open("sample_signature.png", "rb+") as sig:
            signed = PdfWrapper("sample_template_with_signature.pdf").fill(
                {
                    "signature": sig.read()
                },
                flatten=False   # optional, set to True to flatten the filled PDF form
            )

        signed.write("output.pdf")
        ```
    === "Aspect Ratio"
        By default, PyPDFForm preserves a signature image's aspect ratio. To stretch the image to the field bounds, set the `preserve_aspect_ratio` property to `False` on the signature field:

        ```python
        from PyPDFForm import PdfWrapper

        pdf = PdfWrapper("sample_template_with_signature.pdf")
        pdf.widgets["signature"].preserve_aspect_ratio = False
        pdf.fill(
            {
                "signature": "sample_signature.png"
            },
        )

        pdf.write("output.pdf")
        ```
=== "CLI"
    === "data.yaml"
        ```yaml
        signature: sample_signature.png
        ```
    === "aspect_ratio.yaml"
        ```yaml
        signature:
          path: sample_signature.png
          preserve_aspect_ratio: false
        ```
    === "Command"
        ```shell
        pypdfform fill sample_template_with_signature.pdf -f data.yaml -o output.pdf
        ```

## Fill image field

An image field accepts the same input types as a signature field: a file path, an open file object, or a bytes stream.

The examples below use [this PDF](pdfs/sample_template_with_image_field.pdf) and [this image](https://github.com/chinapandaman/PyPDFForm/raw/master/image_samples/sample_image.jpg):

=== "Library"
    === "File Path"
        ```python
        from PyPDFForm import PdfWrapper

        filled = PdfWrapper("sample_template_with_image_field.pdf").fill(
            {
                "image_1": "sample_image.jpg"
            },
            flatten=False   # optional, set to True to flatten the filled PDF form
        )

        filled.write("output.pdf")
        ```
    === "Open File Object"
        ```python
        from PyPDFForm import PdfWrapper

        with open("sample_image.jpg", "rb+") as img:
            filled = PdfWrapper("sample_template_with_image_field.pdf").fill(
                {
                    "image_1": img
                },
                flatten=False   # optional, set to True to flatten the filled PDF form
            )

        filled.write("output.pdf")
        ```
    === "Bytes File Stream"
        ```python
        from PyPDFForm import PdfWrapper

        with open("sample_image.jpg", "rb+") as img:
            filled = PdfWrapper("sample_template_with_image_field.pdf").fill(
                {
                    "image_1": img.read()
                },
                flatten=False   # optional, set to True to flatten the filled PDF form
            )

        filled.write("output.pdf")
        ```
    === "Aspect Ratio"
        Unlike signature fields, image fields are stretched to the field bounds by default. To preserve the original image aspect ratio, set the `preserve_aspect_ratio` property to `True` on the image field:

        ```python
        from PyPDFForm import PdfWrapper

        pdf = PdfWrapper("sample_template_with_image_field.pdf")
        pdf.widgets["image_1"].preserve_aspect_ratio = True
        pdf.fill(
            {
                "image_1": "sample_image.jpg"
            },
        )

        pdf.write("output.pdf")
        ```
=== "CLI"
    === "data.yaml"
        ```yaml
        image_1: sample_image.jpg
        ```
    === "aspect_ratio.yaml"
        ```yaml
        image_1:
          path: sample_image.jpg
          preserve_aspect_ratio: true
        ```
    === "Command"
        ```shell
        pypdfform fill sample_template_with_image_field.pdf -f data.yaml -o output.pdf
        ```
