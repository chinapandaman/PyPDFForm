# -*- coding: utf-8 -*-

from typing import List

from reportlab.pdfgen.canvas import Canvas

from .checkbox import CheckBoxWidget


class RadioWidget(CheckBoxWidget):
    ACRO_FORM_FUNC = "radio"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: List[float],
        y: List[float],
        **kwargs,
    ) -> None:
        self.USER_PARAMS.append(("shape", "shape"))
        super().__init__(name, page_number, x, y, **kwargs)

    def canvas_operations(self, canvas: Canvas) -> None:
        for i, x in enumerate(self.acro_form_params["x"]):
            y = self.acro_form_params["y"][i]
            new_acro_form_params = self.acro_form_params.copy()
            new_acro_form_params["x"] = x
            new_acro_form_params["y"] = y
            new_acro_form_params["value"] = str(i)
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**new_acro_form_params)
