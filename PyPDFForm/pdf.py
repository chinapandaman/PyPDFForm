# -*- coding: utf-8 -*-

import os
import shutil
import uuid
from tempfile import NamedTemporaryFile

import pdfrw
from PIL import Image
from reportlab.pdfgen import canvas as canv


class PyPDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    _LAYER_SIZE_X = 800.27
    _LAYER_SIZE_Y = 841.89

    _CANVAS_FONT = "Helvetica"

    def __init__(self):
        self._uuid = uuid.uuid4().hex
        self._data_dict = {}

        self._canvas = canv
        self._global_font_size = 12
        self._max_txt_length = 100

        self.stream = ""

    def _bool_to_checkboxes(self):
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def _assign_uuid(self, output_stream):
        generated_pdf = pdfrw.PdfReader(fdata=output_stream)

        for i in range(len(generated_pdf.pages)):
            annots = generated_pdf.pages[i][self._ANNOT_KEY]
            if annots:
                for annot in annots:
                    if self._ANNOT_FIELD_KEY in annot.keys():
                        annot.update(
                            pdfrw.PdfDict(
                                T="{}_{}".format(
                                    annot[self._ANNOT_FIELD_KEY][1:-1], self._uuid,
                                ),
                                Ff=pdfrw.PdfObject(1),
                            )
                        )

        with NamedTemporaryFile("w+b", suffix=".pdf") as final_file:
            pdfrw.PdfWriter().write(final_file, generated_pdf)
            final_file.seek(0)
            return final_file.read()

    def _fill_pdf(self, template_stream):
        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        for i in range(len(template_pdf.pages)):
            annots = template_pdf.pages[i][self._ANNOT_KEY]
            if annots:
                for annot in annots:
                    if (
                        annot[self._SUBTYPE_KEY] == self._WIDGET_SUBTYPE_KEY
                        and annot[self._ANNOT_FIELD_KEY]
                    ):
                        key = annot[self._ANNOT_FIELD_KEY][1:-1]
                        if key in self._data_dict.keys():
                            annot.update(
                                pdfrw.PdfDict(
                                    V="{}".format(self._data_dict[key]),
                                    AS=self._data_dict[key],
                                )
                            )

        with NamedTemporaryFile("w+b", suffix=".pdf") as output_file:
            pdfrw.PdfWriter().write(output_file, template_pdf)
            output_file.seek(0)
            return output_file.read()

    def fill(
        self, template_stream, data, canvas=False,
    ):
        self._data_dict = data
        self._bool_to_checkboxes()

        output_stream = self._fill_pdf(template_stream)
        self.stream = self._assign_uuid(output_stream)

        return self
