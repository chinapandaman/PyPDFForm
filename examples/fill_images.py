import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template_with_image_field.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_IMAGE_1 = os.path.join(
    os.path.expanduser("~"), "sample_image.jpg"
)  # Change this to where you downloaded the sample image

PATH_TO_IMAGE_2 = os.path.join(
    os.path.expanduser("~"), "sample_image_2.jpg"
)  # Change this to where you downloaded the sample image

PATH_TO_IMAGE_3 = os.path.join(
    os.path.expanduser("~"), "sample_image_3.jpg"
)  # Change this to where you downloaded the sample image

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_IMAGE_1, "rb+") as image:
    image_stream_1 = image.read()

with open(PATH_TO_IMAGE_2, "rb+") as image:
    image_stream_2 = image.read()

with open(PATH_TO_IMAGE_3, "rb+") as image:
    image_stream_3 = image.read()

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read()).fill(
        {
            "image_1": image_stream_1,
            "image_2": image_stream_2,
            "image_3": image_stream_3,
        },
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
