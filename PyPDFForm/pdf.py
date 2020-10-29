# -*- coding: utf-8 -*-

import os
import shutil
import uuid
from tempfile import TemporaryFile

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

    def _assign_uuid(self, output_file, final_file):
        generated_pdf = pdfrw.PdfReader(output_file.name)

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

        pdfrw.PdfWriter().write(final_file.name, generated_pdf)

    def _fill_pdf(self, template_file, output_file):
        template_pdf = pdfrw.PdfReader(template_file.name)

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

        pdfrw.PdfWriter().write(output_file.name, template_pdf)

    def fill(
        self, template_stream, data, canvas=False,
    ):
        self._data_dict = data
        self._bool_to_checkboxes()

        with TemporaryFile("w+b", suffix=".pdf") as template_file:
            template_file.write(template_stream)

            with TemporaryFile("w+b", suffix=".pdf") as output_file:
                self._fill_pdf(template_file, output_file)

                with TemporaryFile("w+b", suffix=".pdf") as final_file:
                    self._assign_uuid(output_file, final_file)
                    final_file.seek(0)
                    self.stream = final_file.read()
