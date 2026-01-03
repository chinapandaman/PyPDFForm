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
