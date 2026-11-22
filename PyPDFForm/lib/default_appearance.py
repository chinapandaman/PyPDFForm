# -*- coding: utf-8 -*-
"""
Module for changing the default appearance (`/DA`) of variable text fields.

A default appearance is a sequence of PDF content stream operations, such as
`/Helv 12 Tf 0 g`, that sets the font, font size, and color of a field's text.
It is read as tokens rather than split on spaces, so line breaks, repeated
spaces, comments, and operations in any order are understood. A change
rewrites only the operands it replaces and keeps the rest of the string as it
was. A string that can't be read, or that lacks the operation a change needs,
is rejected with an error rather than rewritten into an invalid one.
"""

import re
from typing import List, NamedTuple

# PDF whitespace, then any other character except a delimiter
_TOKEN_PATTERN = re.compile(
    r"(?P<space>[\x00\t\n\x0c\r ]+)"
    r"|(?P<comment>%[^\r\n]*)"
    r"|(?P<name>/[^\x00\t\n\x0c\r ()<>\[\]{}/%]*)"
    r"|(?P<word>[^\x00\t\n\x0c\r ()<>\[\]{}/%]+)"
)
_NUMBER_PATTERN = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)")
# the content stream operators of ISO 32000; any other word is an operand,
# such as a font name written without its slash
_OPERATORS = frozenset(
    {
        *("b", "B", "b*", "B*", "BDC", "BI", "BMC", "BT", "BX", "c", "cm", "CS"),
        *("cs", "d", "d0", "d1", "Do", "DP", "EI", "EMC", "ET", "EX", "f", "F"),
        *("f*", "G", "g", "gs", "h", "i", "ID", "j", "J", "K", "k", "l", "m"),
        *("M", "MP", "n", "q", "Q", "re", "RG", "rg", "ri", "s", "S", "SC", "sc"),
        *("SCN", "scn", "sh", "T*", "Tc", "Td", "TD", "Tf", "Tj", "TJ", "TL"),
        *("Tm", "Tr", "Ts", "Tw", "Tz", "v", "w", "W", "W*", "y", "'", '"'),
    }
)
_FONT_OPERATOR = "Tf"
_RGB_OPERATOR = "rg"
# fill color operators and the number of operands each takes
_COLOR_OPERATORS = {"g": 1, _RGB_OPERATOR: 3, "k": 4}


class _Token(NamedTuple):
    """
    A token of a default appearance string.

    Attributes:
        kind (str): `name`, `number`, `operator`, or `word` for any other
            operand, such as a font name written without its slash.
        start (int): The index of its first character.
        end (int): The index after its last character.
    """

    kind: str
    start: int
    end: int


class _Operation(NamedTuple):
    """
    An operator and the operands before it.

    Attributes:
        operator (str): The operator, such as `Tf`.
        end (int): The index after the operator.
        operands (List[_Token]): Its operands, in order.
    """

    operator: str
    end: int
    operands: List[_Token]


def _parse(default_appearance: object, change: str) -> List[_Operation]:
    """
    Reads the operations of a default appearance string.

    Args:
        default_appearance (object): The resolved `/DA` value.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        List[_Operation]: The operations, in order.

    Raises:
        ValueError: If the value is not a string, has a character that can't
            start a token, such as `(` or `[`, or ends with operands that no
            operator uses.
    """
    if not isinstance(default_appearance, str):
        msg = f"Cannot change the {change}: the field's /DA is not a string."
        # malformed PDF data, raised like every other /DA error
        raise ValueError(msg)  # noqa: TRY004

    operations = []
    operands = []
    position = 0
    while position < len(default_appearance):
        match = _TOKEN_PATTERN.match(default_appearance, position)
        if match is None:
            msg = (
                f"Cannot change the {change}: /DA {default_appearance!r} has an "
                f"unexpected {default_appearance[position]!r}."
            )
            raise ValueError(msg)

        position = match.end()
        text = match.group()
        if match.lastgroup == "name":
            operands.append(_Token("name", match.start(), position))
        elif match.lastgroup != "word":
            continue
        elif _NUMBER_PATTERN.fullmatch(text):
            operands.append(_Token("number", match.start(), position))
        elif text in _OPERATORS:
            operations.append(_Operation(text, position, operands))
            operands = []
        else:
            operands.append(_Token("word", match.start(), position))

    if operands:
        msg = (
            f"Cannot change the {change}: /DA {default_appearance!r} ends with "
            "operands that no operator uses."
        )
        raise ValueError(msg)

    return operations


def _get_font_operations(
    default_appearance: str, operations: List[_Operation], change: str
) -> List[_Operation]:
    """
    Gets the `Tf` operations of a default appearance string.

    Args:
        default_appearance (str): The `/DA` string, for errors.
        operations (List[_Operation]): Its operations.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        List[_Operation]: Every `Tf` operation, each with a font and a size.

    Raises:
        ValueError: If there is no `Tf` operation, or one doesn't have a font
            followed by a numeric size.
    """
    result = [each for each in operations if each.operator == _FONT_OPERATOR]
    if not result:
        msg = (
            f"Cannot change the {change}: /DA {default_appearance!r} has no "
            f"{_FONT_OPERATOR} operator."
        )
        raise ValueError(msg)

    for each in result:
        if (
            len(each.operands) != 2
            or each.operands[0].kind == "number"
            or each.operands[1].kind != "number"
        ):
            msg = (
                f"Cannot change the {change}: the {_FONT_OPERATOR} operator of "
                f"/DA {default_appearance!r} needs a font and a font size."
            )
            raise ValueError(msg)

    return result


def _replace(default_appearance: str, replacements: List[tuple]) -> str:
    """
    Replaces parts of a default appearance string.

    Args:
        default_appearance (str): The `/DA` string.
        replacements (List[tuple]): `(start, end, text)` tuples of parts
            that don't overlap.

    Returns:
        str: The string with each part replaced by its text.
    """
    result = default_appearance
    for start, end, text in sorted(replacements, reverse=True):
        result = result[:start] + text + result[end:]

    return result


def change_font(default_appearance: object, font: str) -> str:
    """
    Changes the font of every `Tf` operation of a default appearance.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font (str): The font resource name, such as `/F1`.

    Returns:
        str: The changed `/DA` string.

    Raises:
        ValueError: If the `/DA` can't be read, or has no `Tf` operation with
            a font and a numeric size.
    """
    operations = _parse(default_appearance, "font")
    return _replace(
        str(default_appearance),
        [
            (each.operands[0].start, each.operands[0].end, font)
            for each in _get_font_operations(
                str(default_appearance), operations, "font"
            )
        ],
    )


def change_font_size(default_appearance: object, font_size: float) -> str:
    """
    Changes the font size of every `Tf` operation of a default appearance.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font_size (float): The font size, where 0 sizes the text to fit.

    Returns:
        str: The changed `/DA` string.

    Raises:
        ValueError: If the `/DA` can't be read, or has no `Tf` operation with
            a font and a numeric size.
    """
    operations = _parse(default_appearance, "font size")
    return _replace(
        str(default_appearance),
        [
            (each.operands[1].start, each.operands[1].end, str(font_size))
            for each in _get_font_operations(
                str(default_appearance), operations, "font size"
            )
        ],
    )


def change_font_color(default_appearance: object, font_color: tuple) -> str:
    """
    Changes the fill color of a default appearance to an RGB color.

    Every gray (`g`), RGB (`rg`), and CMYK (`k`) fill color operation is
    replaced by an `rg` operation with the new color. Without one, an `rg`
    operation is added after the last operation. Other operations, such as
    `Tf` and `Tz`, are kept.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font_color (tuple): The RGB color, each component from 0 to 1.

    Returns:
        str: The changed `/DA` string.

    Raises:
        ValueError: If the `/DA` can't be read, or a fill color operation
            doesn't have the number of numeric operands it takes.
    """
    operations = _parse(default_appearance, "font color")
    default_appearance = str(default_appearance)
    color = " ".join(str(each) for each in font_color) + f" {_RGB_OPERATOR}"

    replacements = []
    for each in operations:
        count = _COLOR_OPERATORS.get(each.operator)
        if count is None:
            continue
        if len(each.operands) != count or any(
            operand.kind != "number" for operand in each.operands
        ):
            msg = (
                f"Cannot change the font color: the {each.operator} operator of "
                f"/DA {default_appearance!r} needs {count} "
                f"{'number' if count == 1 else 'numbers'}."
            )
            raise ValueError(msg)
        replacements.append((each.operands[0].start, each.end, color))

    if not replacements:
        end = operations[-1].end if operations else 0
        replacements.append((end, end, f" {color}" if operations else color))

    return _replace(default_appearance, replacements)
