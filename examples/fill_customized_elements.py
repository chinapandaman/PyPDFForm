import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    pdf_form = PyPDFForm(template.read(), simple_mode=False)

    pdf_form.elements["test"].font_size = 20
    pdf_form.elements["test"].font_color = (1, 0, 0)
    pdf_form.elements["test_2"].text_x_offset = 50
    pdf_form.elements["test_2"].text_y_offset = -50
    pdf_form.elements["test_2"].text_wrap_length = 1
    pdf_form.elements["test_2"].font_color = (0, 1, 0)
    pdf_form.elements["test_3"].text_wrap_length = 2
    pdf_form.elements["test_3"].font_color = (0, 0, 1)

    pdf_form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(pdf_form.stream)
