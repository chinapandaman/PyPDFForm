import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template_sejda.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, sejda=True)
        .fill(
            {
                "date": "01-01",
                "year": "21",
                "buyer_name": "John Doe",
                "buyer_address": "1 N Main St, Chicago, IL 60000",
                "seller_name": "Jack Smith",
                "seller_address": "2 S Main St, Chicago, IL 60000",
                "make": "AK",
                "model": "47",
                "caliber": "7.62-x39mm",
                "serial_number": "111111",
                "purchase_option": 0,
                "date_of_this_bill": True,
                "at_future_date": True,
                "other": True,
                "other_reason": "NO REASONS",
                "payment_amount": "400",
                "future_date": "01-01",
                "future_year": "22",
                "exchange_for": "Food",
                "buyer_name_printed": "John Doe",
                "seller_name_printed": "Jack Smith",
                "buyer_signed_date": "2021-01-01",
                "seller_signed_date": "2021-01-01",
                "buyer_dl_number": "D000-4609-0001",
                "seller_dl_number": "S530-4209-0001",
                "buyer_dl_state": "IL",
                "seller_dl_state": "IL",
            },
        )
        .read()
    )
