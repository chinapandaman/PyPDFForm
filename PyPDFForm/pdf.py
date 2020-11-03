# -*- coding: utf-8 -*-

import uuid
from io import BytesIO
from typing import Union

import pdfrw
from PIL import Image
from PyPDFForm.exceptions import (
    InvalidFontSizeError,
    InvalidFormDataError,
    InvalidImageCoordinateError,
    InvalidImageDimensionError,
    InvalidImageError,
    InvalidImageRotationAngleError,
    InvalidModeError,
    InvalidPageNumberError,
    InvalidTemplateError,
    InvalidWrapLengthError,
)
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as canv


class _PyPDFForm(object):
    def __init__(self) -> None:
        self._ANNOT_KEY = "/Annots"
        self._ANNOT_FIELD_KEY = "/T"
        self._ANNOT_RECT_KEY = "/Rect"
        self._SUBTYPE_KEY = "/Subtype"
        self._WIDGET_SUBTYPE_KEY = "/Widget"

        self._CANVAS_FONT = "Helvetica"
        self._GLOBAL_FONT_SIZE = 12
        self._MAX_TXT_LENGTH = 100

        self._data_dict = {}

        self.stream = b""

    def __add__(self, other: "_PyPDFForm") -> "_PyPDFForm":
        if not self.stream:
            return other

        self._validate_template(self.stream)
        self._validate_template(other.stream)

        writer = pdfrw.PdfWriter()

        writer.addpages(pdfrw.PdfReader(fdata=self.stream).pages)
        writer.addpages(pdfrw.PdfReader(fdata=other.stream).pages)

        result_stream = BytesIO()
        writer.write(result_stream)
        result_stream.seek(0)

        new_obj = self.__class__()
        new_obj.stream = result_stream.read()

        result_stream.close()

        return new_obj

    @staticmethod
    def _validate_template(template_stream: bytes) -> None:
        if b"%PDF" not in template_stream:
            raise InvalidTemplateError

    @staticmethod
    def _validate_fill_inputs(
        data: dict,
        simple_mode: bool,
        font_size: Union[float, int],
        text_wrap_length: int,
    ) -> None:
        if not isinstance(data, dict):
            raise InvalidFormDataError

        if not isinstance(simple_mode, bool):
            raise InvalidModeError

        if not (isinstance(font_size, float) or isinstance(font_size, int)):
            raise InvalidFontSizeError

        if not isinstance(text_wrap_length, int):
            raise InvalidWrapLengthError

    @staticmethod
    def _validate_draw_image_inputs(
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int],
    ) -> None:
        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not (isinstance(x, float) or isinstance(x, int)):
            raise InvalidImageCoordinateError

        if not (isinstance(y, float) or isinstance(y, int)):
            raise InvalidImageCoordinateError

        if not (isinstance(width, float) or isinstance(width, int)):
            raise InvalidImageDimensionError

        if not (isinstance(height, float) or isinstance(height, int)):
            raise InvalidImageDimensionError

        if not (isinstance(rotation, float) or isinstance(rotation, int)):
            raise InvalidImageRotationAngleError

    def _bool_to_checkboxes(self) -> None:
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def _assign_uuid(self, output_stream: bytes) -> bytes:
        _uuid = uuid.uuid4().hex

        generated_pdf = pdfrw.PdfReader(fdata=output_stream)

        for i in range(len(generated_pdf.pages)):
            annotations = generated_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for annotation in annotations:
                    if self._ANNOT_FIELD_KEY in annotation.keys():
                        annotation.update(
                            pdfrw.PdfDict(
                                T="{}_{}".format(
                                    annotation[self._ANNOT_FIELD_KEY][1:-1], _uuid,
                                ),
                                Ff=pdfrw.PdfObject(1),
                            )
                        )

        result_stream = BytesIO()
        pdfrw.PdfWriter().write(result_stream, generated_pdf)
        result_stream.seek(0)

        result = result_stream.read()
        result_stream.close()

        return result

    def _fill_pdf(self, template_stream: bytes) -> bytes:
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

        result_stream = BytesIO()
        pdfrw.PdfWriter().write(result_stream, template_pdf)
        result_stream.seek(0)

        result = result_stream.read()

        result_stream.close()

        return result

    def _fill_pdf_canvas(
        self,
        template_stream: bytes,
        text_x_offset: Union[float, int],
        text_y_offset: Union[float, int],
    ) -> bytes:
        template_pdf = pdfrw.PdfReader(fdata=template_stream)
        layers = []

        for i in range(len(template_pdf.pages)):
            layer = BytesIO()
            layers.append(layer)

            c = canv.Canvas(
                layer,
                pagesize=(
                    float(template_pdf.pages[i].MediaBox[2]),
                    float(template_pdf.pages[i].MediaBox[3]),
                ),
            )
            c.setFont(self._CANVAS_FONT, self._GLOBAL_FONT_SIZE)

            annotations = template_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for j in reversed(range(len(annotations))):
                    annotation = annotations[j]

                    if (
                        annotation[self._SUBTYPE_KEY] == self._WIDGET_SUBTYPE_KEY
                        and annotation[self._ANNOT_FIELD_KEY]
                    ):
                        key = annotation[self._ANNOT_FIELD_KEY][1:-1]
                        if key in self._data_dict.keys():
                            if self._data_dict[key] in [
                                pdfrw.PdfName.Yes,
                                pdfrw.PdfName.Off,
                            ]:
                                annotation.update(
                                    pdfrw.PdfDict(
                                        AS=self._data_dict[key], Ff=pdfrw.PdfObject(1)
                                    )
                                )
                            else:
                                coordinates = annotation[self._ANNOT_RECT_KEY]
                                annotations.pop(j)
                                if len(self._data_dict[key]) < self._MAX_TXT_LENGTH:
                                    c.drawString(
                                        float(coordinates[0]) + text_x_offset,
                                        (float(coordinates[1]) + float(coordinates[3]))
                                        / 2
                                        - 2
                                        + text_y_offset,
                                        self._data_dict[key],
                                    )
                                else:
                                    txt_obj = c.beginText(0, 0)

                                    start = 0
                                    end = self._MAX_TXT_LENGTH

                                    while end < len(self._data_dict[key]):
                                        txt_obj.textLine(
                                            (self._data_dict[key][start:end])
                                        )
                                        start += self._MAX_TXT_LENGTH
                                        end += self._MAX_TXT_LENGTH
                                    txt_obj.textLine(self._data_dict[key][start:])
                                    c.saveState()
                                    c.translate(
                                        float(coordinates[0]),
                                        (float(coordinates[1]) + float(coordinates[3]))
                                        / 2
                                        - 2,
                                    )
                                    c.drawText(txt_obj)
                                    c.restoreState()
                        else:
                            annotations.pop(j)

            c.save()
            layer.seek(0)

        for i in range(len(template_pdf.pages)):
            layer_pdf = pdfrw.PdfReader(layers[i])
            input_page = template_pdf.pages[i]
            merger = pdfrw.PageMerge(input_page)

            if len(layer_pdf.pages) > 0:
                merger.add(layer_pdf.pages[0]).render()

            layers[i].close()

        result_stream = BytesIO()
        pdfrw.PdfWriter().write(result_stream, template_pdf)
        result_stream.seek(0)

        result = result_stream.read()
        result_stream.close()

        return result

    def draw_image(
        self,
        image_stream: bytes,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int],
    ) -> "_PyPDFForm":
        self._validate_template(self.stream)
        self._validate_draw_image_inputs(page_number, x, y, width, height, rotation)

        input_file = pdfrw.PdfReader(fdata=self.stream)

        buff = BytesIO()
        buff.write(image_stream)
        buff.seek(0)

        try:
            image = Image.open(buff)
        except Exception:
            raise InvalidImageError

        image_buff = BytesIO()
        image.rotate(rotation, expand=True).save(image_buff, format=image.format)
        image_buff.seek(0)

        canv_buff = BytesIO()

        c = canv.Canvas(
            canv_buff,
            pagesize=(
                float(input_file.pages[page_number - 1].MediaBox[2]),
                float(input_file.pages[page_number - 1].MediaBox[3]),
            ),
        )

        c.drawImage(ImageReader(image_buff), x, y, width=width, height=height)
        c.save()
        canv_buff.seek(0)

        output_file = pdfrw.PdfFileWriter()

        for i in range(len(input_file.pages)):
            if i == page_number - 1:
                merger = pdfrw.PageMerge(input_file.pages[i])
                merger.add(pdfrw.PdfReader(fdata=canv_buff.read()).pages[0]).render()

        result_stream = BytesIO()
        output_file.write(result_stream, input_file)
        result_stream.seek(0)
        self.stream = result_stream.read()

        buff.close()
        image_buff.close()
        canv_buff.close()
        result_stream.close()

        return self

    def fill(
        self,
        template_stream: bytes,
        data: dict,
        simple_mode: bool,
        font_size: Union[float, int],
        text_x_offset: Union[float, int],
        text_y_offset: Union[float, int],
        text_wrap_length: int,
    ) -> "_PyPDFForm":
        self._validate_template(template_stream)
        self._validate_fill_inputs(data, simple_mode, font_size, text_wrap_length)

        self._GLOBAL_FONT_SIZE = font_size
        self._MAX_TXT_LENGTH = text_wrap_length

        self._data_dict = data
        self._bool_to_checkboxes()

        if simple_mode:
            output_stream = self._fill_pdf(template_stream)
            self.stream = self._assign_uuid(output_stream)
        else:
            self.stream = self._fill_pdf_canvas(
                template_stream, text_x_offset, text_y_offset
            )

        return self
