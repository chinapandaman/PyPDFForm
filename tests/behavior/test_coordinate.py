# -*- coding: utf-8 -*-


from PyPDFForm import BlankPage, Fields, PdfWrapper


def test_widget_coord_resolution():
    obj = PdfWrapper(BlankPage()).bulk_create_fields(
        [
            Fields.TextField("text", 1, 50, 100, width=200, height=150),
            Fields.CheckBoxField("check", 1, 150, 200, size=60),
            Fields.RadioGroup("radio", 1, [400, 500, 600], [450, 550, 650], size=10),
            Fields.DropdownField(
                "dropdown", 1, 400, 100, width=250, height=200, options=["foo", "bar"]
            ),
            Fields.ImageField("image", 1, 300, 400, width=400, height=300),
            Fields.SignatureField("signature", 1, 500, 600, width=600, height=500),
        ]
    )

    assert obj.widgets["text"].page_number == 1
    assert obj.widgets["text"].x == 50
    assert obj.widgets["text"].y == 100
    assert obj.widgets["text"].width == 200
    assert obj.widgets["text"].height == 150

    assert obj.widgets["check"].page_number == 1
    assert obj.widgets["check"].x == 150
    assert obj.widgets["check"].y == 200
    assert obj.widgets["check"].width == 60
    assert obj.widgets["check"].height == 60

    assert obj.widgets["radio"].page_number == 1
    assert obj.widgets["radio"].x == [400, 500, 600]
    assert obj.widgets["radio"].y == [450, 550, 650]
    assert obj.widgets["radio"].width == [10, 10, 10]
    assert obj.widgets["radio"].height == [10, 10, 10]

    assert obj.widgets["dropdown"].page_number == 1
    assert obj.widgets["dropdown"].x == 400
    assert obj.widgets["dropdown"].y == 100
    assert obj.widgets["dropdown"].width == 250
    assert obj.widgets["dropdown"].height == 200

    assert obj.widgets["image"].page_number == 1
    assert obj.widgets["image"].x == 300
    assert obj.widgets["image"].y == 400
    assert obj.widgets["image"].width == 400
    assert obj.widgets["image"].height == 300

    assert obj.widgets["signature"].page_number == 1
    assert obj.widgets["signature"].x == 500
    assert obj.widgets["signature"].y == 600
    assert obj.widgets["signature"].width == 600
    assert obj.widgets["signature"].height == 500
