# PDF coordinate system

The PDF coordinate system originates at the bottom left of the page. The unit of measurement is "points," with 72 points per inch. PyPDFForm uses this coordinate system in its APIs to create fields, text, and images on a PDF.

## Generate a coordinate grid view

To enhance the user experience with the coordinate system, PyPDFForm provides a grid view that helps determine the optimal placement of elements on a PDF.

To generate a coordinate grid view for [this PDF](pdfs/sample_template.pdf), use the following code:

```python
from PyPDFForm import PdfWrapper

grid_view_pdf = PdfWrapper("sample_template.pdf").generate_coordinate_grid(
    color=(1, 0, 0),    # optional
    margin=100  # optional
)

grid_view_pdf.write("output.pdf")
```

The `generate_coordinate_grid` method accepts two optional parameters: `color` and `margin`. The `color` parameter sets the grid view color (defaulting to red), and the `margin` parameter adjusts the coordinate grid view's margin in points (defaulting to 100 points).

## Inspect form field coordinates & dimensions

You can inspect the coordinates and dimensions of a PDF form field's rectangular bounding box by accessing its widget object:

```python
from PyPDFForm import PdfWrapper

form = PdfWrapper("sample_template.pdf")

print(form.widgets["test"].x)
print(form.widgets["test"].y)
print(form.widgets["test"].width)
print(form.widgets["test"].height)
```
