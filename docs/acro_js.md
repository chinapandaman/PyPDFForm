# Embed PDF JavaScript

???+ warning
    Do NOT trust user input; always sanitize it. Although PDF JavaScript runs in a sandbox, arbitrary execution is dangerous and can lead to remote code execution vulnerabilities.

These examples use [sample_template.pdf](pdfs/sample_template.pdf).

PDFs can execute JavaScript during interactions if supported by the viewer. PyPDFForm provides APIs to embed scripts into both the PDF document and its form fields.

The examples below embed a script that displays an alert when the pointer hovers over the `test` field:

=== "Library"
    === "alert.js"
        ```javascript
        app.alert("Hello World!");
        ```
    === "File Path"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_hovered_over_javascript = "./alert.js"

        form.write("output.pdf")
        ```
    === "File Object"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_hovered_over_javascript = open("./alert.js")  # in practice, use a context manager

        form.write("output.pdf")
        ```
    === "File Content"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_hovered_over_javascript = open("./alert.js").read()  # in practice, use a context manager

        form.write("output.pdf")
        ```
=== "CLI"
    Set the field-level JavaScript property in JSON and pass it to `update field`:

    === "alert.js"
        ```javascript
        app.alert("Hello World!");
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_hovered_over_javascript": "./alert.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

???+ tip
    For supported Acrobat JavaScript APIs, see the [Adobe JavaScript API reference](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html).

## Execute JavaScript on hover

Set `on_hovered_over_javascript` to run code when the pointer hovers over a field:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "hovered over";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_hovered_over_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "hovered over";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_hovered_over_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript when hover ends

Set `on_hovered_off_javascript` to run code when the pointer leaves a field:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "hovered off";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_hovered_off_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "hovered off";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_hovered_off_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript on mouse press

Set `on_mouse_pressed_javascript` to run code when a mouse button is pressed inside a field:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "mouse pressed";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_mouse_pressed_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "mouse pressed";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_mouse_pressed_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript on mouse release

Set `on_mouse_released_javascript` to run code when a mouse button is released inside a field:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "mouse released";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_mouse_released_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "mouse released";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_mouse_released_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript on focus

Set `on_focused_javascript` to run code when a field gains focus:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "focused";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_focused_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "focused";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_focused_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript on blur

Set `on_blurred_javascript` to run code when a field loses focus:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "not focused";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.widgets["test"].on_blurred_javascript = "./script.js"

        form.write("output.pdf")
        ```
=== "CLI"
    Set the same field-level JavaScript property in JSON and pass it to `update field`:

    === "script.js"
        ```javascript
        this.getField("test").value = "not focused";
        ```
    === "data.json"
        ```json
        {
            "test": {
                "on_blurred_javascript": "./script.js"
            }
        }
        ```
    === "Command"
        ```shell
        pypdfform update field sample_template.pdf -f data.json -o output.pdf
        ```

## Execute JavaScript on PDF open

Use `PdfWrapper.on_open_javascript` to set or read the script that runs when the PDF opens:

=== "Library"
    === "script.js"
        ```javascript
        this.getField("test").value = "opened";
        ```
    === "main.py"
        ```python
        from PyPDFForm import PdfWrapper

        form = PdfWrapper("sample_template.pdf")
        form.on_open_javascript = "./script.js"
        print(form.on_open_javascript)

        form.write("output.pdf")
        ```
=== "CLI"
    Use `update script` to set document-level JavaScript that runs when the PDF opens:

    === "script.js"
        ```javascript
        this.getField("test").value = "opened";
        ```
    === "Command"
        ```shell
        pypdfform update script sample_template.pdf -s script.js -o output.pdf
        ```
