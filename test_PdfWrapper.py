from PyPDFForm import PdfWrapper
from io import BytesIO
import tempfile
import icecream as ic


pdf = PdfWrapper(r"pdf_samples\sample_template.pdf")

# Write to a file

# PdfWrapper implements itself similar to an open file object.
# So you can write the PDF it holds to another file:

with open("output1.pdf", "wb+") as output:
    pdf_bytes = pdf.read()  # Make sure this is the correct method to get the PDF data as bytes.
    if pdf_bytes is not None:  # Always good to check if the content is not None
        output.write(pdf_bytes)
    else:
        print("Failed to get PDF content.")
    
# # And it doesn't have to be a disk file, it can be a memory buffer as well:

with BytesIO() as output:
    pdf_bytes = pdf.read()  # Assuming pdf.read() correctly returns the PDF data as bytes.
    if pdf_bytes is not None:
        output.write(pdf_bytes)
        output.seek(0)  # Go back to the start if you plan to read from it
        # Now you can use 'output' as needed, for example, sending it over a network, saving elsewhere, etc.
    else:
        print("Failed to get PDF content.")


# PDF coordinates
# The coordinate system on a single page of a PDF starts at the bottom left of the page as the origin. 
# The units of the coordinates are called "points" and there are 72 points/inch. 
# PyPDFForm utilizes this coordinate system in some of its APIs so that widgets, texts, or images can be created on a PDF.

# Generate a coordinate grid view
# To allow a better user experience with the coordinate system, 
# PyPDFForm implements a grid view so that there is a better idea on where stuffs should be placed on a PDF.


# grid_view_pdf = PdfWrapper(
#     (r"pdf_samples\sample_template.pdf")
# ).generate_coordinate_grid(color=(1, 0, 0))

# with open("output2.pdf", "wb+") as output:
#     output.write(grid_view_pdf.read())
    
    
# Path to your PDF file
pdf_path = "pdf_samples\dummy.pdf"

# Read the PDF file and get the data in bytes
with open(pdf_path, "rb") as f:
    pdf_data = f.read()

# Create a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
    temp_pdf.write(pdf_data)
    temp_path = temp_pdf.name

# Create a PdfWrapper object with the temporary file
pdf_form = PdfWrapper(temp_path)

# Create the first widget
new_checkbox_widget = pdf_form.create_widget(
    widget_type="checkbox",
    name="new_checkbox_widget",
    page_number=1,
    x=57,
    y=700,
    size=30,
    button_style="check"
)

# Create another widget
new_text_field_widget = pdf_form.create_widget(
    widget_type="text",
    name="new_text_field_widget",
    page_number=1,
    x=100,
    y=700,
    width=120,
    height=40,
    max_length=5,
    font="Courier",
    font_size=15,
    font_color=(1, 0, 0)
)

# Path to your output file
output_path = "output6.pdf"

# Copy the temporary file to the output file
with open(temp_path, "rb") as temp_file, open(output_path, "wb+") as output:
    output.write(temp_file.read())
    
    
preview_stream = PdfWrapper(r"pdf_samples\sample_template.pdf").preview

with open("output7.pdf", "wb+") as output:
    output.write(preview_stream)
    

import json

pdf_form_schema = PdfWrapper(r"pdf_samples\sample_template.pdf").schema

# print(json.dumps(pdf_form_schema, indent=4, sort_keys=True))


from pprint import pprint

pprint(PdfWrapper(r"pdf_samples\sample_template.pdf").sample_data)
