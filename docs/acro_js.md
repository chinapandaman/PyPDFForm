# Embed field JavaScript (beta)

???+ info
    This section contains beta features, which means both the features themselves and the documentations are undergoing constant changes. Please use these features with caution as they may be changed or even rollback in the future and they may not work for some PDF forms.

This section of the documentation will primarily use [this PDF](pdfs/sample_template.pdf) as an example.

PDF form fields allow executions of JavaScript when certain interactions happen, if the viewer/editor supports. PyPDFForm provides a simple set of APIs that enables embedding JavaScript code into each form field.

For example, the following snippet shows how you can embed a script that, when the text field `test` is hovered over, pops up an alert box:

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
    form.widgets["test"].on_hovered_over_javascript = open("./alert.js")

    form.write("output.pdf")
    ```
=== "File Content"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    form.widgets["test"].on_hovered_over_javascript = open("./alert.js").read()

    form.write("output.pdf")
    ```

???+ tip
    Please refer [here](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html) for JavaScript that can be executed in PDF forms.

## Execute JavaScript on hovered over

As seen in the previous example, you can embed your JavaScript code to the `on_hovered_over_javascript` attribute of each field, which will make it run when the field is hovered over by the mouse cursor:

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

## Execute JavaScript on hovered off

Setting the `on_hovered_off_javascript` attribute runs the JavaScript code embedded to a form field when the mouse cursor moves away from it:

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

Setting the `on_mouse_pressed_javascript` attribute runs the JavaScript code embedded to a form field when the mouse button is pressed down within the field:

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

Setting the `on_mouse_released_javascript` attribute runs the JavaScript code embedded to a form field when the mouse button is released within the field:

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

## Execute JavaScript on focused

Setting the `on_focused_javascript` attribute runs the JavaScript code embedded to a form field when the it's focused, as in selected by your mouse:

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

## Execute JavaScript off focused

Setting the `off_focused_javascript` attribute runs the JavaScript code embedded to a form field when the it's no longer focused:

=== "script.js"
    ```javascript
    this.getField("test").value = "not focused";
    ```
=== "main.py"
    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")
    form.widgets["test"].off_focused_javascript = "./script.js"

    form.write("output.pdf")
    ```
