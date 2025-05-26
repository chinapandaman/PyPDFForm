# PDF coordinate system

The PDF coordinate system originates at the bottom left of the page. The unit of measurement is "points," with 72 points per inch. PyPDFForm uses this coordinate system in its APIs to create fields, text, and images on a PDF.

## Generate a coordinate grid view

To enhance the user experience with the coordinate system, PyPDFForm provides a grid view that helps determine the optimal placement of elements on a PDF.

To generate a coordinate grid view for [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), use the following code:

```python
from PyPDFForm import PdfWrapper

grid_view_pdf = PdfWrapper("sample_template.pdf").generate_coordinate_grid(
    color=(1, 0, 0),    # optional
    margin=100  # optional
)

grid_view_pdf.write("output.pdf")
```

The `generate_coordinate_grid` method accepts two optional parameters: `color` and `margin`. The `color` parameter sets the grid view color (defaulting to red), and the `margin` parameter adjusts the coordinate grid view's margin in points (defaulting to 100 points).
