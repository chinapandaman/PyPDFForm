# -*- coding: utf-8 -*-

import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile

import pdfrw
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as canv


class PyPDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    _LAYER_SIZE_X = 800.27
    _LAYER_SIZE_Y = 841.89

    def __init__(self):
        self._uuid = uuid.uuid4().hex
        self._data_dict = {}

        self.stream = ""

    def _bool_to_checkboxes(self):
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def _assign_uuid(self, output_stream):
        generated_pdf = pdfrw.PdfReader(fdata=output_stream)

        for i in range(len(generated_pdf.pages)):
            annotations = generated_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for annotation in annotations:
                    if self._ANNOT_FIELD_KEY in annotation.keys():
                        annotation.update(
                            pdfrw.PdfDict(
                                T="{}_{}".format(
                                    annotation[self._ANNOT_FIELD_KEY][1:-1], self._uuid,
                                ),
                                Ff=pdfrw.PdfObject(1),
                            )
                        )

        with NamedTemporaryFile(suffix=".pdf") as final_file:
            pdfrw.PdfWriter().write(final_file, generated_pdf)
            final_file.seek(0)
            return final_file.read()

    def _fill_pdf(self, template_stream):
        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        for i in range(len(template_pdf.pages)):
            annotations = template_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for annotation in annotations:
                    if (
                        annotation[self._SUBTYPE_KEY] == self._WIDGET_SUBTYPE_KEY
                        and annotation[self._ANNOT_FIELD_KEY]
                    ):
                        key = annotation[self._ANNOT_FIELD_KEY][1:-1]
                        if key in self._data_dict.keys():
                            annotation.update(
                                pdfrw.PdfDict(
                                    V="{}".format(self._data_dict[key]),
                                    AS=self._data_dict[key],
                                )
                            )

        with NamedTemporaryFile(suffix=".pdf") as output_file:
            pdfrw.PdfWriter().write(output_file, template_pdf)
            output_file.seek(0)
            return output_file.read()

    def draw_image(self, page_number, image_stream, x, y, width, height, rotation=0):
        buff = BytesIO()
        buff.write(image_stream)
        buff.seek(0)

        image = Image.open(buff)

        image_buff = BytesIO()
        image.rotate(rotation, expand=True).save(image_buff, format="JPEG")
        image_buff.seek(0)

        canv_buff = BytesIO()

        c = canv.Canvas(canv_buff, pagesize=(self._LAYER_SIZE_X, self._LAYER_SIZE_Y))

        c.drawImage(ImageReader(image_buff), x, y, width=width, height=height)
        c.save()
        canv_buff.seek(0)

        output_file = pdfrw.PdfFileWriter()

        input_file = pdfrw.PdfReader(fdata=self.stream)

        for i in range(len(input_file.pages)):
            if i == page_number - 1:
                merger = pdfrw.PageMerge(input_file.pages[i])
                merger.add(pdfrw.PdfReader(fdata=canv_buff.read()).pages[0]).render()

        with NamedTemporaryFile(suffix=".pdf") as f:
            output_file.write(f, input_file)
            f.seek(0)
            self.stream = f.read()

            return self

    def fill(self, template_stream, data):
        self._data_dict = data
        self._bool_to_checkboxes()

        output_stream = self._fill_pdf(template_stream)
        self.stream = self._assign_uuid(output_stream)

        return self
