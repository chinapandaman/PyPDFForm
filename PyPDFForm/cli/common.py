# -*- coding: utf-8 -*-
"""
Common utilities for the PyPDFForm CLI.

This module provides common helper functions used across various
CLI commands, such as handling font registration and creating
elements from file definitions.
"""

import json

import typer

from .. import PdfWrapper


def handle_font_registration(
    obj: PdfWrapper, params: dict, registered_font: dict
) -> None:
    """
    Registers a font if it is not already registered.

    This function checks if a font is specified in the parameters.
    If it is, and it hasn't been registered yet, it generates a new
    font name, registers the font with the PdfWrapper object, and
    adds it to the registered_font dictionary. It then updates the
    parameters with the newly registered font name.

    Args:
        obj (PdfWrapper): The PdfWrapper object to register the font with.
        params (dict): A dictionary of parameters for the element,
            which may contain a "font" key specifying the path to a TTF file.
        registered_font (dict): A dictionary tracking already registered fonts,
            mapping the original font path to the registered font name.
    """
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
    """
    Creates elements on a PDF form using data loaded from a JSON file.

    This function reads a JSON file containing element definitions,
    processes them (including registering any required fonts), and
    calls a specified method on a PdfWrapper object to create the elements
    on the PDF. Finally, it writes the modified PDF to the specified output path
    or overwrites the original file if no output path is provided.

    Args:
        pdf (str): The path to the input PDF file.
        data (str): The path to the JSON file containing element definitions.
        element_map (dict): A dictionary mapping element types (keys in the JSON file)
            to their corresponding classes or construction functions.
        method_name (str): The name of the method to call on the PdfWrapper object
            to create the elements (e.g., 'bulk_create_fields', 'draw').
        ctx (typer.Context): The Typer context, used to access global options
            like `use_full_widget_name` or `need_appearances` to initialize the PdfWrapper.
        output (str, optional): The path where the modified PDF should be saved.
            If None, the input PDF file will be overwritten. Defaults to None.
    """
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
