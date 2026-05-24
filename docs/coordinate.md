# PDF coordinate system

The PDF coordinate system originates at the bottom left of the page. The unit of measurement is "points," with 72 points per inch. PyPDFForm uses this coordinate system in its APIs to create fields, text, and images on a PDF.

## Generate a coordinate grid view

To make PDF coordinates easier to work with, PyPDFForm provides a grid view that helps you determine the optimal placement of elements on a PDF.

To generate a coordinate grid view for [this PDF](pdfs/sample_template.pdf):

=== "Library"
    Use the `PdfWrapper.generate_coordinate_grid` method:

    ```python
    from PyPDFForm import PdfWrapper

    grid_view_pdf = PdfWrapper("sample_template.pdf").generate_coordinate_grid(
        color=(1, 0, 0),    # optional
        margin=100  # optional
    )

    grid_view_pdf.write("output.pdf")
    ```

    The `generate_coordinate_grid` method accepts two optional parameters: `color` and `margin`. The `color` parameter sets the grid color (defaulting to red), and the `margin` parameter sets the grid margin in points (defaulting to 100 points).

=== "CLI"
    Use the `create grid` command:

    ```shell
    pypdfform create grid sample_template.pdf -r 1 -g 0 -b 0 -m 100 -o output.pdf
    ```

    As with the library API, the `-r`, `-g`, and `-b` options are optional and set the grid color. The `-m` option sets the margin.

## Inspect form field locations & dimensions

=== "Library"
    You can inspect the location and dimensions of a PDF form field's rectangular bounding box by accessing its widget object:

    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")

    print(form.widgets["test"].page_number)
    print(form.widgets["test"].x)
    print(form.widgets["test"].y)
    print(form.widgets["test"].width)
    print(form.widgets["test"].height)
    ```
=== "CLI"
    To inspect a field with the CLI, use `inspect location` and pass the field name with `--field`:

    ```shell
    pypdfform inspect location sample_template.pdf --field test
    ```

## Change form field coordinates & dimensions

???+ tip
    For a checkbox or radio button, consider modifying [size](style.md#change-checkboxradio-button-size) instead of `width` or `height`.

=== "Library"
    You can modify these same attributes to reposition or resize the field's rectangular bounding box:

    ```python
    from PyPDFForm import PdfWrapper

    form = PdfWrapper("sample_template.pdf")

    form.widgets["test"].x = 68.3365
    form.widgets["test"].y = 657.692
    form.widgets["test"].width = 242.4235
    form.widgets["test"].height = 31.067999999999984

    form.write("output.pdf")
    ```
=== "CLI"
    Use the `update bounds` command with options that specify the field and the coordinates or dimensions to change:

    ```shell
    pypdfform update bounds sample_template.pdf \
        --field test \
        --x 68.3365 \
        --y 657.692 \
        --width 242.4235 \
        --height 31.067999999999984 \
        -o output.pdf
    ```
