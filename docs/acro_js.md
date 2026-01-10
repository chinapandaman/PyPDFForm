# Embed field JavaScript (beta)

???+ info
    These beta features and their documentation are subject to change. Use with caution; they may be modified, rolled back, or fail in some PDF forms.

???+ warning
    Do NOT trust user input; always sanitize it. Although PDF JavaScript runs in a sandbox, arbitrary execution is dangerous and can lead to remote code execution vulnerabilities.

This documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

PDF form fields can execute JavaScript during interactions if supported by the viewer. PyPDFForm provides APIs to embed scripts into form fields.

For example, this snippet embeds a script that triggers an alert when the `test` field is hovered:

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

???+ tip
    Please refer to [this link](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html) for JavaScript that can be executed in PDF forms.

## Execute JavaScript on hover

Set the `on_hovered_over_javascript` attribute to run code when a field is hovered over:

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

## Execute JavaScript on hover off

Set the `on_hovered_off_javascript` attribute to run code when the mouse moves away from a field:

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

## Execute JavaScript on mouse pressed

Set the `on_mouse_pressed_javascript` attribute to run code when a mouse button is pressed within a field:

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

## Execute JavaScript on mouse released

Set the `on_mouse_released_javascript` attribute to run code when a mouse button is released within a field:

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

## Execute JavaScript on focus

Set the `on_focused_javascript` attribute to run code when a field gains focus:

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

## Execute JavaScript on blur

Set the `on_blurred_javascript` attribute to run code when a field loses focus:

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

## Execute JavaScript on PDF open

Set the `on_open_javascript` attribute of the `PdfWrapper` object to run code when the PDF is opened:

=== "script.js"
    ```javascript
    this.getField("test").value = "opened";
    ```
=== "main.py"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    form.on_open_javascript = "./script.js"

    form.write("output.pdf")
    ```
