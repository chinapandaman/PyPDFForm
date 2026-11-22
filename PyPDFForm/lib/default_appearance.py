# -*- coding: utf-8 -*-
"""
Module for changing the default appearance (`/DA`) of variable text fields.

A default appearance is a sequence of PDF content stream operations, such as
`/Helv 12 Tf 0 g`, that sets the font, font size, and color of a field's text.
It is read as tokens rather than split on spaces, so line breaks, repeated
spaces, comments, array operands such as a dash pattern, and operations in any
order are understood. A change rewrites only the operands it replaces and keeps
the rest of the string as it was, and writes numbers and names that the next
change can read. A string that can't be read, or that lacks the operation a
change needs, is rejected with an error rather than rewritten into an invalid
one.
"""

import re
from collections.abc import Iterator
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import List, NamedTuple

# PDF whitespace, then any other character except a delimiter
_TOKEN_PATTERN = re.compile(
    r"(?P<space>[\x00\t\n\x0c\r ]+)"
    r"|(?P<comment>%[^\r\n]*)"
    r"|(?P<name>/[^\x00\t\n\x0c\r ()<>\[\]{}/%]*)"
    r"|(?P<word>[^\x00\t\n\x0c\r ()<>\[\]{}/%]+)"
    r"|(?P<open>\[)"
    r"|(?P<close>\])"
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
# fill color operators that set a color, and the number of operands each takes
_COLOR_OPERATORS = {"g": 1, _RGB_OPERATOR: 3, "k": 4}
# every operator that changes the fill color, including through a color space
_FILL_COLOR_OPERATORS = frozenset({"cs", "sc", "scn", *_COLOR_OPERATORS})


class _Token(NamedTuple):
    """
    A token of a default appearance string.

    Attributes:
        kind (str): `operator`, or the kind of an operand: `name`, `number`,
            `array` for a whole array, including any arrays in it, or `word`
            for any other operand, such as a font name written without its
            slash.
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


def to_text(default_appearance: object, change: str) -> str:
    """
    Gets a resolved `/DA` value as text.

    A string that pypdf can't decode as text, such as one with a NUL
    character, which is PDF whitespace, is a byte string. Its bytes are read as
    Latin-1, which maps each byte to the character with the same code, so the
    text can be encoded back to the same bytes.

    Args:
        default_appearance (object): The resolved `/DA` value.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        str: The `/DA` string.

    Raises:
        ValueError: If the value is not a string.
    """
    if isinstance(default_appearance, bytes):
        return default_appearance.decode("latin-1")
    if not isinstance(default_appearance, str):
        msg = f"Cannot change the {change}: the field's /DA is not a string."
        # malformed PDF data, raised like every other /DA error
        raise ValueError(msg)  # noqa: TRY004

    return default_appearance


def _tokenize(default_appearance: str, change: str) -> Iterator[_Token]:
    """
    Reads the tokens of a default appearance string.

    Whitespace and comments are skipped, and an array, with any arrays in it,
    is one token.

    Args:
        default_appearance (str): The `/DA` string.
        change (str): What is being changed, such as `font size`, for errors.

    Yields:
        _Token: Each operator and operand, in order.

    Raises:
        ValueError: If the string has a character that can't start a token,
            such as `(`, or an unbalanced `[` or `]`.
    """
    array_start = 0
    depth = 0
    position = 0
    while position < len(default_appearance):
        match = _TOKEN_PATTERN.match(default_appearance, position)
        if match is None or (match.lastgroup == "close" and not depth):
            msg = (
                f"Cannot change the {change}: /DA {default_appearance!r} has an "
                f"unexpected {default_appearance[position]!r}."
            )
            raise ValueError(msg)

        position = match.end()
        if match.lastgroup == "open":
            if not depth:
                array_start = match.start()
            depth += 1
        elif match.lastgroup == "close":
            depth -= 1
            if not depth:
                yield _Token("array", array_start, position)
        elif not depth and match.lastgroup == "name":
            yield _Token("name", match.start(), position)
        elif not depth and match.lastgroup == "word":
            text = match.group()
            kind = (
                "number"
                if _NUMBER_PATTERN.fullmatch(text)
                else "operator"
                if text in _OPERATORS
                else "word"
            )
            yield _Token(kind, match.start(), position)

    if depth:
        msg = (
            f"Cannot change the {change}: /DA {default_appearance!r} has an "
            "unclosed '['."
        )
        raise ValueError(msg)


def _parse(default_appearance: str, change: str) -> List[_Operation]:
    """
    Reads the operations of a default appearance string.

    Args:
        default_appearance (str): The `/DA` string.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        List[_Operation]: The operations, in order.

    Raises:
        ValueError: If the string can't be read as tokens, or ends with
            operands that no operator uses.
    """
    operations = []
    operands = []
    for token in _tokenize(default_appearance, change):
        if token.kind == "operator":
            operations.append(
                _Operation(
                    default_appearance[token.start : token.end], token.end, operands
                )
            )
            operands = []
        else:
            operands.append(token)

    if operands:
        msg = (
            f"Cannot change the {change}: /DA {default_appearance!r} ends with "
            "operands that no operator uses."
        )
        raise ValueError(msg)

    return operations


def _format_number(value: object, change: str) -> str:
    """
    Writes a number in the decimal form of a PDF number.

    A value whose text already has that form, such as `12` or `30.5`, is
    written as it is, and other numbers, such as `1e-05`, without an exponent.

    Args:
        value (object): The number.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        str: The number as PDF text.

    Raises:
        ValueError: If the value has no decimal form, such as infinity.
    """
    text = str(value)
    if not _NUMBER_PATTERN.fullmatch(text):
        with suppress(InvalidOperation):
            text = format(Decimal(text), "f")

    if not _NUMBER_PATTERN.fullmatch(text):
        msg = f"Cannot change the {change}: {value!r} is not a number a PDF can store."
        raise ValueError(msg)

    return text


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
            or each.operands[0].kind not in ("name", "word")
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
        ValueError: If the `/DA` can't be read, has no `Tf` operation with a
            font and a numeric size, or the font is not a single PDF name,
            such as one with a space.
    """
    text = to_text(default_appearance, "font")
    operations = _parse(text, "font")
    match = _TOKEN_PATTERN.fullmatch(font)
    if match is None or match.lastgroup != "name":
        msg = f"Cannot change the font: {font!r} is not a PDF name."
        raise ValueError(msg)

    return _replace(
        text,
        [
            (each.operands[0].start, each.operands[0].end, font)
            for each in _get_font_operations(text, operations, "font")
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
        ValueError: If the `/DA` can't be read, has no `Tf` operation with a
            font and a numeric size, or the size has no decimal form.
    """
    text = to_text(default_appearance, "font size")
    operations = _parse(text, "font size")
    size = _format_number(font_size, "font size")

    return _replace(
        text,
        [
            (each.operands[1].start, each.operands[1].end, size)
            for each in _get_font_operations(text, operations, "font size")
        ],
    )


def change_font_color(default_appearance: object, font_color: tuple) -> str:
    """
    Changes the fill color of a default appearance to an RGB color.

    Every gray (`g`), RGB (`rg`), and CMYK (`k`) fill color operation is
    replaced by an `rg` operation with the new color. When the last operation
    that changes the fill color is not one of these, such as an `sc` or a `cs`
    that sets a color space, or there is none, an `rg` operation is added
    after it, or after the last operation, so the new color takes effect.
    Other operations, such as `Tf` and `Tz`, are kept.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font_color (tuple): The RGB color, each component from 0 to 1.

    Returns:
        str: The changed `/DA` string.

    Raises:
        ValueError: If the `/DA` can't be read, a gray, RGB, or CMYK fill
            color operation doesn't have the number of numeric operands it
            takes, or a component has no decimal form.
    """
    text = to_text(default_appearance, "font color")
    operations = _parse(text, "font color")
    color = (
        " ".join(_format_number(each, "font color") for each in font_color)
        + f" {_RGB_OPERATOR}"
    )

    replacements = []
    last = None
    for each in operations:
        if each.operator not in _FILL_COLOR_OPERATORS:
            continue
        last = each
        count = _COLOR_OPERATORS.get(each.operator)
        if count is None:
            continue
        if len(each.operands) != count or any(
            operand.kind != "number" for operand in each.operands
        ):
            msg = (
                f"Cannot change the font color: the {each.operator} operator of "
                f"/DA {text!r} needs {count} "
                f"{'number' if count == 1 else 'numbers'}."
            )
            raise ValueError(msg)
        replacements.append((each.operands[0].start, each.end, color))

    if last is None or last.operator not in _COLOR_OPERATORS:
        if last is None and operations:
            last = operations[-1]
        if last is None:
            replacements.append((0, 0, color))
        else:
            replacements.append((last.end, last.end, f" {color}"))

    return _replace(text, replacements)
