import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm()

    for i in range(3):
        filled_pdf += PyPDFForm(template.read()).fill(
            {
                "test": "{}_test_1".format(i),
                "check": True,
                "test_2": "{}_test_2".format(i),
                "check_2": False,
                "test_3": "{}_test_3".format(i),
                "check_3": True,
            },
        )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
