"""
ModuShell: Terminal Styling Toolkit

This module provides a simple interface for applying ANSI styles, text effects,
and color formatting (RGB, HSL, HEX, and 8-bit) to terminal output using Python.

Author: Kenneth Irving
License: MIT
Repository: https://github.com/irvingkennet45/ModuShell
"""

import json
import os

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "8bit_colors.json"), "r") as f:
    COLOR_MAP = json.load(f)

START_CODE_EXT = "\033["
SGR_VARIABLE_EXT = "m"
END_CODE_EXT = "\033[0" + SGR_VARIABLE_EXT

End = END_CODE_EXT


def color_handle(variable: str | tuple[int, int, int]) -> str:
    """
    Converts a HEX string, RGB tuple, or HSL tuple into an ANSI color string.

    Args:
        variable (str | tuple[int, int, int]): A HEX string like "#ffffff",
        an RGB tuple like (255, 0, 0), or an HSL tuple like (180, 0.5, 0.5).

    Returns:
        str: ANSI escape sequence representing the color.

    Raises:
        ValueError: If the input is not a valid HEX, RGB, or HSL format.
    """
    def rgb_handle(r, g, b):
        return f"{int(r)};{int(g)};{int(b)}{SGR_VARIABLE_EXT}"

    def hsl_handle(h, s, l):
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p

        if h > 1:
            h = (h % 360) / 360

        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)

        return f"{round(r * 255)};{round(g * 255)};{round(b * 255)}{SGR_VARIABLE_EXT}"

    def hex_handle(hex_code):
        hex_code = hex_code.lstrip('#')
        rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
        return f"{rgb[0]};{rgb[1]};{rgb[2]}{SGR_VARIABLE_EXT}"

    if '#' in variable:
        return hex_handle(variable)
    elif 0 <= variable[0] <= 360 and 0 < variable[1] < 1 and 0 < variable[2] < 1:
        return hsl_handle(*variable)
    elif all(0 <= v <= 255 for v in variable):
        return rgb_handle(*variable)
    else:
        raise ValueError("Invalid color input: must be RGB tuple, HSL tuple, or hex string.")


def Color(input_color):
    """
    Shortcut to call color_handle directly.

    Args:
        input_color: HEX, RGB, or HSL format.

    Returns:
        str: ANSI escape sequence.
    """
    return color_handle(input_color)


def Italic() -> str:
    """Returns ANSI sequence to italicize text."""
    return f"{START_CODE_EXT}3{SGR_VARIABLE_EXT}"


class Weight:
    """Text weight styling options."""

    def BOLD() -> str:
        """Returns ANSI sequence for bold text."""
        return f"{START_CODE_EXT}1{SGR_VARIABLE_EXT}"

    def LIGHT() -> str:
        """Returns ANSI sequence for light text."""
        return f"{START_CODE_EXT}2{SGR_VARIABLE_EXT}"


class Line:
    """Underline, overline, and underline removal options."""

    def OVER() -> str:
        """Returns ANSI sequence for overline text."""
        return f"{START_CODE_EXT}53{SGR_VARIABLE_EXT}"

    def UNDER(amnt: int) -> str:
        """
        Returns ANSI sequence for underline text.

        Args:
            amnt (int): 1 for single underline, 2 for double underline.

        Returns:
            str: ANSI escape sequence.

        Raises:
            ValueError: If amnt is not 1 or 2.
        """
        if amnt == 1:
            return f"{START_CODE_EXT}4{SGR_VARIABLE_EXT}"
        if amnt == 2:
            return f"{START_CODE_EXT}21{SGR_VARIABLE_EXT}"
        raise ValueError("UNDER() expects 1 or 2. Got: {}".format(amnt))

    def RM() -> str:
        """Returns ANSI sequence to remove underline."""
        return f"{START_CODE_EXT}24{SGR_VARIABLE_EXT}"


def Cross() -> str:
    """Returns ANSI sequence for strikethrough text."""
    return f"{START_CODE_EXT}9{SGR_VARIABLE_EXT}"


def Frame() -> str:
    """Returns ANSI sequence to frame text."""
    return f"{START_CODE_EXT}51{SGR_VARIABLE_EXT}"


def Circle() -> str:
    """Returns ANSI sequence to encircle text."""
    return f"{START_CODE_EXT}52{SGR_VARIABLE_EXT}"


class Blink:
    """Text blinking options."""

    def SLOW() -> str:
        """Returns ANSI sequence for slow blinking text."""
        return f"{START_CODE_EXT}5{SGR_VARIABLE_EXT}"

    def FAST() -> str:
        """Returns ANSI sequence for fast blinking text."""
        return f"{START_CODE_EXT}6{SGR_VARIABLE_EXT}"

    def OFF() -> str:
        """Returns ANSI sequence to stop blinking."""
        return f"{START_CODE_EXT}25{SGR_VARIABLE_EXT}"


def Big2(amount: int) -> str:
    """
    Combines underline and bold styles.

    Args:
        amount (int): 1 or 2 for underline style.

    Returns:
        str: ANSI escape sequence.
    """
    return Line.UNDER(amount) + Weight.BOLD()


def Big3(amount: int) -> str:
    """
    Combines underline, bold, and italic styles.

    Args:
        amount (int): 1 or 2 for underline style.

    Returns:
        str: ANSI escape sequence.
    """
    return Line.UNDER(amount) + Weight.BOLD() + Italic()


class Colorize:
    """Colorize text or background using ANSI escape sequences."""

    def FONT(color: str | tuple[int, int, int]) -> str:
        """
        Returns ANSI sequence for foreground color.

        Args:
            color: HEX, RGB, or HSL.

        Returns:
            str: ANSI escape sequence.
        """
        return f"{START_CODE_EXT}38;2;{color_handle(color)}"

    def HIGH(color: str | tuple[int, int, int]) -> str:
        """
        Returns ANSI sequence for background color.

        Args:
            color: HEX, RGB, or HSL.

        Returns:
            str: ANSI escape sequence.
        """
        return f"{START_CODE_EXT}48;2;{color_handle(color)}"

    def FONT8(color_name: str, set_type: str = "main_colors") -> str:
        """
        Returns 8-bit foreground color from color map.

        Args:
            color_name: Name of the color.
            set_type: Color set group.

        Returns:
            str: ANSI escape sequence.
        """
        try:
            code = COLOR_MAP[set_type][color_name]["fg"]
            return f"{START_CODE_EXT}{code}{SGR_VARIABLE_EXT}"
        except KeyError:
            raise ValueError(f"Color '{color_name}' not found in {set_type}")

    def HIGH8(color_name: str, set_type: str = "main_colors") -> str:
        """
        Returns 8-bit background color from color map.

        Args:
            color_name: Name of the color.
            set_type: Color set group.

        Returns:
            str: ANSI escape sequence.
        """
        try:
            code = COLOR_MAP[set_type][color_name]["bg"]
            return f"{START_CODE_EXT}{code}{SGR_VARIABLE_EXT}"
        except KeyError:
            raise ValueError(f"Color '{color_name}' not found in {set_type}")


def RESET() -> str:
    """Returns ANSI reset sequence to clear all formatting."""
    return END_CODE_EXT


__all__ = [
    "Italic", "Cross", "Frame", "Circle", "Blink",
    "Weight", "Line", "Big2", "Big3", "Colorize",
    "Color", "RESET", "End"
]
