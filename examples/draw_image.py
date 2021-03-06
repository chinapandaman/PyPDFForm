import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

PATH_TO_IMAGE = os.path.join(
    os.path.expanduser("~"), "sample_image.jpeg"
)  # Change this to the location of an image of your choice

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .draw_image(PATH_TO_IMAGE, 2, 100, 100, 400, 225, 0)
        .read()
    )
