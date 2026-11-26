# -*- coding: utf-8 -*-
"""
Module for reading and changing the default appearance (`/DA`) of variable
text fields.

A default appearance is a sequence of PDF content stream operations, such as
`/Helv 12 Tf 0 g`, that sets the font, font size, and color of a field's text.
It is read as tokens rather than split on spaces, so line breaks, repeated
spaces, comments, array operands such as a dash pattern, and operations in any
order are understood. A change rewrites only the operands it replaces and keeps
the rest of the string as it was, and writes numbers and names that the next
change can read. A string that can't be read, or that lacks the operation a
change needs, is rejected with an error rather than rewritten into an invalid
one; reading such a string gives no value instead.
"""

import re
from collections.abc import Callable, Iterator
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import List, NamedTuple, Optional

from pypdf.generic import NameObject

# PDF whitespace, a comment, a name, a run of other characters that aren't
# delimiters, such as a number or an operator, an array or dictionary
# bracket, a hexadecimal string, or the start of a literal string
_TOKEN_PATTERN = re.compile(
    r"(?P<space>[\x00\t\n\x0c\r ]+)"
    r"|(?P<comment>%[^\r\n]*)"
    r"|(?P<name>/[^\x00\t\n\x0c\r ()<>\[\]{}/%]*)"
    r"|(?P<word>[^\x00\t\n\x0c\r ()<>\[\]{}/%]+)"
    r"|(?P<open>\[|<<)"
    r"|(?P<close>\]|>>)"
    r"|(?P<hex><[0-9A-Fa-f\x00\t\n\x0c\r ]*>)"
    r"|(?P<string>\()"
)
# the closing bracket of each array or dictionary bracket, and the kind of
# the operand it encloses
_CONTAINERS = {"[": ("]", "array"), "<<": (">>", "dictionary")}
# ASCII digits only, since \d also matches the digits of other scripts
_NUMBER_PATTERN = re.compile(r"[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)")
# a # in a name that isn't followed by two hex digits, or that escapes NUL
_INVALID_NAME_ESCAPE = re.compile(r"#(?![0-9A-Fa-f]{2})|#00")
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
# the gray, RGB, and CMYK fill color operators, and the operands each takes
_COLOR_OPERAND_COUNTS = {"g": 1, _RGB_OPERATOR: 3, "k": 4}
# every operator that changes the fill color, including through a color space
_FILL_COLOR_OPERATORS = frozenset({"cs", "sc", "scn", *_COLOR_OPERAND_COUNTS})


class _Token(NamedTuple):
    """
    A token of a default appearance string.

    Attributes:
        kind (str): `operator`, or the kind of an operand: `name`, `number`,
            `string` for a literal or hexadecimal string, `array` for a whole
            array or `dictionary` for a whole dictionary, including anything
            in it, or `word` for any other operand, such as a font name
            written without its slash.
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


def _tokenize(default_appearance: str, change: str) -> Iterator[_Token]:
    """
    Reads the tokens of a default appearance string.

    Whitespace and comments are skipped. A literal or hexadecimal string is
    one token, and so is an array or a dictionary, with anything in it.

    Args:
        default_appearance (str): The `/DA` string.
        change (str): What is being changed, such as `font size`, for errors.

    Yields:
        _Token: Each operator and operand, in order.

    Raises:
        ValueError: If the string has a character that can't start a token,
            such as `{`, a bracket that doesn't close the innermost open
            array or dictionary, or an unclosed string, array, or dictionary.
    """
    containers: List[str] = []
    container_start = 0
    position = 0
    while position < len(default_appearance):
        match = _TOKEN_PATTERN.match(default_appearance, position)
        if match is None or (
            match.lastgroup == "close"
            and (not containers or _CONTAINERS[containers[-1]][0] != match.group())
        ):
            msg = (
                f"Cannot change the {change}: /DA {default_appearance!r} has an "
                f"unexpected {default_appearance[position]!r}."
            )
            raise ValueError(msg)

        start = match.start()
        position = (
            _skip_literal_string(default_appearance, position, change)
            if match.lastgroup == "string"
            else match.end()
        )
        if match.lastgroup == "open":
            if not containers:
                container_start = start
            containers.append(match.group())
        elif match.lastgroup == "close":
            kind = _CONTAINERS[containers.pop()][1]
            if not containers:
                yield _Token(kind, container_start, position)
        elif not containers and match.lastgroup in ("hex", "string"):
            yield _Token("string", start, position)
        elif not containers and match.lastgroup == "name":
            yield _Token("name", start, position)
        elif not containers and match.lastgroup == "word":
            yield _Token(_get_word_kind(match.group()), start, position)

    if containers:
        msg = (
            f"Cannot change the {change}: /DA {default_appearance!r} has an "
            f"unclosed {containers[-1]!r}."
        )
        raise ValueError(msg)


def _skip_literal_string(default_appearance: str, position: int, change: str) -> int:
    """
    Finds the end of a literal string, such as `(a \\) (b) c)`.

    Parentheses in it are balanced unless escaped with a backslash, which
    also escapes a backslash, as ISO 32000-1 specifies.

    Args:
        default_appearance (str): The `/DA` string.
        position (int): The index of the string's opening parenthesis.
        change (str): What is being changed, such as `font size`, for errors.

    Returns:
        int: The index after its closing parenthesis.

    Raises:
        ValueError: If the string isn't closed.
    """
    depth = 0
    while position < len(default_appearance):
        character = default_appearance[position]
        if character == "\\":
            position += 1
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if not depth:
                return position + 1
        position += 1

    msg = f"Cannot change the {change}: /DA {default_appearance!r} has an unclosed '('."
    raise ValueError(msg)


def _get_word_kind(text: str) -> str:
    """
    Gets the kind of a token that is neither a name nor an array.

    Args:
        text (str): The token's text.

    Returns:
        str: `number`, `operator`, or `word` for any other operand.
    """
    if _NUMBER_PATTERN.fullmatch(text):
        return "number"

    return "operator" if text in _OPERATORS else "word"


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
    written as it is, and other numbers, such as `1e-05` or `１２` written
    with digits other than ASCII, are written in that form, as `0.00001` and
    `12`.

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


def _has_font_and_size(operation: _Operation) -> bool:
    """
    Checks whether a `Tf` operation has a font followed by a numeric size.

    Args:
        operation (_Operation): The `Tf` operation.

    Returns:
        bool: True if its operands are a font, with or without its slash, and
            a number.
    """
    return (
        len(operation.operands) == 2
        and operation.operands[0].kind in ("name", "word")
        and operation.operands[1].kind == "number"
    )


def _has_color_operands(operation: _Operation) -> bool:
    """
    Checks whether a gray, RGB, or CMYK fill color operation has its operands.

    Args:
        operation (_Operation): A `g`, `rg`, or `k` operation.

    Returns:
        bool: True if it has the number of numeric operands it takes.
    """
    return len(operation.operands) == _COLOR_OPERAND_COUNTS[operation.operator] and all(
        operand.kind == "number" for operand in operation.operands
    )


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
        if not _has_font_and_size(each):
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


def _decode(default_appearance: object) -> str | None:
    """
    Reads a resolved `/DA` value as a string.

    A string that pypdf can't decode as text, such as one with a NUL
    character, which is PDF whitespace, is a byte string. Its bytes are read as
    Latin-1, which maps each byte to the character with the same code. A PDF
    name isn't a string, although pypdf reads it as a `str`.

    Args:
        default_appearance (object): The resolved `/DA` value.

    Returns:
        str | None: The `/DA` string, or None when the value is not a string.
    """
    if isinstance(default_appearance, NameObject):
        return None
    if isinstance(default_appearance, bytes):
        return default_appearance.decode("latin-1")
    if isinstance(default_appearance, str):
        return default_appearance

    return None


def _rewrite(
    default_appearance: object,
    change: str,
    get_replacements: Callable[[str, List[_Operation]], List[tuple]],
) -> str | bytes:
    """
    Replaces parts of a resolved `/DA` value, keeping its type.

    A byte string is read as `_decode` describes, and the result is encoded
    the same way, so the bytes outside the replaced parts don't change.

    Args:
        default_appearance (object): The resolved `/DA` value.
        change (str): What is being changed, such as `font size`, for errors.
        get_replacements (Callable[[str, List[_Operation]], List[tuple]]):
            Returns the `(start, end, text)` replacements for the `/DA` string
            and its operations.

    Returns:
        str | bytes: The changed `/DA`, as bytes when it was a byte string.

    Raises:
        ValueError: If the value is not a string or can't be read.
    """
    text = _decode(default_appearance)
    if text is None:
        msg = f"Cannot change the {change}: the field's /DA is not a string."
        # malformed PDF data, raised like every other /DA error
        raise ValueError(msg)

    result = _replace(text, get_replacements(text, _parse(text, change)))
    return result.encode("latin-1") if isinstance(default_appearance, bytes) else result


def _replace_font_operands(
    default_appearance: object, change: str, index: int, replacement: str
) -> str | bytes:
    """
    Replaces an operand of every `Tf` operation of a default appearance.

    Args:
        default_appearance (object): The resolved `/DA` value.
        change (str): What is being changed, such as `font size`, for errors.
        index (int): The operand to replace: 0 for the font, 1 for the size.
        replacement (str): The operand's new text.

    Returns:
        str | bytes: The changed `/DA`, as bytes when it was a byte string.

    Raises:
        ValueError: If the `/DA` can't be read, or has no `Tf` operation with a
            font and a numeric size.
    """
    return _rewrite(
        default_appearance,
        change,
        lambda text, operations: [
            (each.operands[index].start, each.operands[index].end, replacement)
            for each in _get_font_operations(text, operations, change)
        ],
    )


def change_font(default_appearance: object, font: str) -> str | bytes:
    """
    Changes the font of every `Tf` operation of a default appearance.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font (str): The font resource name, such as `/F1`.

    Returns:
        str | bytes: The changed `/DA`, as bytes when it was a byte string.

    Raises:
        ValueError: If the font is not a single PDF name written in ASCII, such
            as one with a space or a character outside ASCII, which a name
            writes as an escape such as `#20`, or has a `#` that isn't followed
            by two hex digits, or `#00`, or the `/DA` can't be read or has no
            `Tf` operation with a font and a numeric size.
    """
    # pypdf writes a /DA with characters outside its text encoding as UTF-16
    match = _TOKEN_PATTERN.fullmatch(font)
    if (
        match is None
        or match.lastgroup != "name"
        or not font.isascii()
        or _INVALID_NAME_ESCAPE.search(font)
    ):
        msg = (
            f"Cannot change the font: {font!r} is not a PDF name written in "
            "ASCII, with each # followed by two hex digits other than 00, such "
            "as #20 for a space."
        )
        raise ValueError(msg)

    return _replace_font_operands(default_appearance, "font", 0, font)


def change_font_size(default_appearance: object, font_size: float) -> str | bytes:
    """
    Changes the font size of every `Tf` operation of a default appearance.

    Args:
        default_appearance (object): The resolved `/DA` value.
        font_size (float): The font size, where 0 sizes the text to fit.

    Returns:
        str | bytes: The changed `/DA`, as bytes when it was a byte string.

    Raises:
        ValueError: If the size has no decimal form, or the `/DA` can't be
            read or has no `Tf` operation with a font and a numeric size.
    """
    return _replace_font_operands(
        default_appearance, "font size", 1, _format_number(font_size, "font size")
    )


def _get_color_replacements(
    default_appearance: str, operations: List[_Operation], color: str
) -> List[tuple]:
    """
    Gets the replacements that change the fill color of a default appearance.

    Args:
        default_appearance (str): The `/DA` string, for errors.
        operations (List[_Operation]): Its operations.
        color (str): The `rg` operation that sets the new color.

    Returns:
        List[tuple]: The `(start, end, text)` replacements.

    Raises:
        ValueError: If a gray, RGB, or CMYK fill color operation doesn't have
            the number of numeric operands it takes.
    """
    replacements = []
    last = None
    for each in operations:
        if each.operator not in _FILL_COLOR_OPERATORS:
            continue
        last = each
        count = _COLOR_OPERAND_COUNTS.get(each.operator)
        if count is None:
            continue
        if not _has_color_operands(each):
            msg = (
                f"Cannot change the font color: the {each.operator} operator of "
                f"/DA {default_appearance!r} needs {count} "
                f"{'number' if count == 1 else 'numbers'}."
            )
            raise ValueError(msg)
        replacements.append((each.operands[0].start, each.end, color))

    # without a fill color operation, the color goes after the last operation
    if last is None and operations:
        last = operations[-1]
    if last is None:
        replacements.append((0, 0, color))
    elif last.operator not in _COLOR_OPERAND_COUNTS:
        replacements.append((last.end, last.end, f" {color}"))

    return replacements


def change_font_color(default_appearance: object, font_color: tuple) -> str | bytes:
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
        font_color (tuple): The RGB color, each component from 0 to 1, as a
            tuple or list of three numbers.

    Returns:
        str | bytes: The changed `/DA`, as bytes when it was a byte string.

    Raises:
        ValueError: If the color doesn't have three components, or a component
            has no decimal form, or the `/DA` can't be read, or a gray, RGB, or
            CMYK fill color operation doesn't have the number of numeric
            operands it takes.
    """
    if not isinstance(font_color, (tuple, list)) or len(font_color) != 3:
        msg = (
            f"Cannot change the font color: {font_color!r} is not an RGB color "
            "with three components."
        )
        raise ValueError(msg)
    color = (
        " ".join(_format_number(each, "font color") for each in font_color)
        + f" {_RGB_OPERATOR}"
    )

    return _rewrite(
        default_appearance,
        "font color",
        lambda text, operations: _get_color_replacements(text, operations, color),
    )


class TextStyle(NamedTuple):
    """
    The font, font size, and font color that a default appearance sets.

    Attributes:
        font (Optional[str]): The font resource name, as the `/DA` writes it,
            such as `/Helv` or `/My#20Font`.
        font_size (Optional[float]): The font size, where 0 sizes the text to
            fit.
        font_color (Optional[tuple]): The fill color, as an RGB tuple.
    """

    font: Optional[str]
    font_size: Optional[float]
    font_color: Optional[tuple]


def read_default_appearance(default_appearance: object) -> TextStyle:
    """
    Reads the font, font size, and font color of a default appearance.

    The last `Tf` operation sets the font and font size, and the last
    operation that changes the fill color sets the color, as for the text a
    viewer draws. A gray (`g`) or CMYK (`k`) color is converted to RGB as
    ISO 32000-1 specifies: a gray level `v` is `(v, v, v)`, and a CMYK color
    `(c, m, y, k)` is `(1 - min(1, c + k), 1 - min(1, m + k), 1 - min(1, y + k))`.
    Each is None when the `/DA` doesn't set it, or sets it in a way that can't
    be read, such as a `Tf` without a numeric size, or a color set through a
    color space with `sc`. A value that isn't a string, or a string that can't
    be read, such as one with `{`, sets none of them. A whole number reads as
    an int, such as `12` or `12.0`, and any other number as a float.

    Args:
        default_appearance (object): The resolved `/DA` value, or None.

    Returns:
        TextStyle: The font, font size, and font color, each None when the
            `/DA` doesn't set it.
    """
    font = font_size = font_color = None
    text = _decode(default_appearance)
    if text is None:
        return TextStyle(font, font_size, font_color)

    operations = []
    with suppress(ValueError):
        operations = _parse(text, "default appearance")

    fonts = [each for each in operations if each.operator == _FONT_OPERATOR]
    if fonts and _has_font_and_size(fonts[-1]):
        name, size = fonts[-1].operands
        font = text[name.start : name.end]
        font_size = _read_number(text[size.start : size.end])

    colors = [each for each in operations if each.operator in _FILL_COLOR_OPERATORS]
    if (
        colors
        and colors[-1].operator in _COLOR_OPERAND_COUNTS
        and _has_color_operands(colors[-1])
    ):
        font_color = _read_rgb_color(text, colors[-1])

    return TextStyle(font, font_size, font_color)


def _read_rgb_color(default_appearance: str, operation: _Operation) -> tuple:
    """
    Reads a gray, RGB, or CMYK fill color operation as an RGB color.

    The components are computed as exact fractions, so the result doesn't
    depend on the caller's decimal context.

    Args:
        default_appearance (str): The `/DA` string.
        operation (_Operation): A `g`, `rg`, or `k` operation with its
            numeric operands.

    Returns:
        tuple: The red, green, and blue components.
    """
    values = [
        Fraction(default_appearance[each.start : each.end])
        for each in operation.operands
    ]
    if operation.operator == "g":
        values *= 3
    elif operation.operator == "k":
        black = values[3]
        values = [1 - min(Fraction(1), each + black) for each in values[:3]]

    return tuple(_to_number(each) for each in values)


def _read_number(text: str) -> float:
    """
    Reads the text of a PDF number.

    Args:
        text (str): The number's text, such as `12` or `.5`.

    Returns:
        float: The number, as an int when it is whole.
    """
    return _to_number(Fraction(text))


def _to_number(value: Fraction) -> float:
    """
    Converts an exact number to an int when it is whole, or to a float.

    Args:
        value (Fraction): The number.

    Returns:
        float: The number, as an int when it is whole.
    """
    return int(value) if value.denominator == 1 else float(value)
