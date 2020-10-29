# -*- coding: utf-8 -*-

import uuid
from tempfile import NamedTemporaryFile

import pdfrw


class PyPDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

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

    def fill(self, template_stream, data):
        self._data_dict = data
        self._bool_to_checkboxes()

        output_stream = self._fill_pdf(template_stream)
        self.stream = self._assign_uuid(output_stream)

        return self
