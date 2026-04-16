# -*- coding: utf-8 -*-

import json

import typer

from .. import PdfWrapper


def handle_font_registration(
    obj: PdfWrapper, params: dict, registered_font: dict
) -> None:
    if "font" in params:
        if params["font"] not in registered_font:
            font_name = f"new_font_{len(registered_font)}"
            obj.register_font(font_name, params["font"])
            registered_font[params["font"]] = font_name
        params["font"] = registered_font[params["font"]]


def create_elements_from_file(
    pdf: str,
    data: str,
    element_map: dict,
    method_name: str,
    ctx: typer.Context,
    output: str = None,
) -> None:
    with open(data, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    obj = PdfWrapper(pdf, **ctx.obj)
    ungrouped_input = []
    registered_font = {}
    for k, v in input_data.items():
        for each in v:
            handle_font_registration(obj, each, registered_font)
            ungrouped_input.append(element_map[k](**each))

    getattr(obj, method_name)(ungrouped_input).write(output or pdf)
