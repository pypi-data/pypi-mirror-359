'''
# This is the core logic for the ModuShell Package
# Description:
# ModuShell is a package that you can use to customize any outputs to the console using simple calls within format strings.
# Requires a modern terminal that can handle ANSI escape sequences.

# ModuShell is licensed under the MIT License, and adheres to the clauses stated within.
# Credit/attribution within any distributed or modified works is required.
# For more information, visit https://opensource.org/license/mit, or this repository's version.
# If you received this software and a license was not included within, please contact contact.kenneth.irving@gmail.com with more details.

# See the README.md for more information

# Developed by Kenneth Irving (irvingkennet45)
# Project Repository: https://github.com/irvingkennet45/ModuShell
'''

import json
import os

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "8bit_colors.json"), "r") as f:
    COLOR_MAP = json.load(f)

START_CODE_EXT = "\033[" # This is the start of all ANSI escape codes (at least the ones used in this program). This snippet is added to the wrappers before the wrappers applicable code is printed
SGR_VARIABLE_EXT = "m" # Inserts the standard SGR (Select Graphic Rendition) variable extension. This defines that we are changing the graphical look in the terminal, rather than the functionality.
END_CODE_EXT = "\033[0" + SGR_VARIABLE_EXT # This is the end of all ANSI escape codes and resets the text to normal. This snippet is added to the wrappers as a constant variable.

End = END_CODE_EXT
# Color Handle: Allows the user to specify colors, no matter the format. It should convert all colors into RGB form automatically. Create a variable, give it either a string value for hex or 3 integer values for HSL and RGB,
# and then call the function with the variable nested.
def color_handle(variable):
	def rgb_handle(r, g, b):
		r = int(r)
		g = int(g)
		b = int(b)
		return str(r) + ";" + str(g) + ";" + str(b) + SGR_VARIABLE_EXT
	def hsl_handle(h, s, l):
		def hue_to_rgb(p, q, t):
			if t < 0:   t += 1
			if t > 1:   t -= 1
			if t < 1 / 6: return p + (q - p) * 6 * t
			if t < 1 / 2: return q
			if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
			return p

		# Normalize hue if using degrees
		if h > 1:
			h = (h % 360) / 360

		if s == 0:
			r = g = b = l  # Achromatic (gray)
		else:
			q = l * (1 + s) if l < 0.5 else l + s - l * s
			p = 2 * l - q
			r = hue_to_rgb(p, q, h + 1 / 3)
			g = hue_to_rgb(p, q, h)
			b = hue_to_rgb(p, q, h - 1 / 3)

		return (f"{round(r * 255)};" + f"{round(g * 255)};" + f"{round(b * 255)}" + SGR_VARIABLE_EXT)
	def hex_handle(hex_code):
		hex_code = hex_code.lstrip('#')
		rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
		return f"{rgb[0]};{rgb[1]};{rgb[2]}{SGR_VARIABLE_EXT}"
	if '#' in variable:
		return (
				hex_handle(variable)
		)
	elif 0 <= variable[0] <= 360 and 0 < variable[1] < 1 and 0 < variable[2] < 1:
		h = variable[0]
		s = variable[1]
		l = variable[2]
		return (
				hsl_handle(h, s, l)
		)
	elif all(0 <= v <= 255 for v in (variable)):
		return (
				rgb_handle(variable[0], variable[1], variable[2])
		)
	else:
		return ValueError
def Color(input_color):
	return color_handle(input_color)

# ------Standard Wrappers------

# Italic Wrapper: Italicizes outputs printed to the console.
def Italic():
	return f"{START_CODE_EXT}3{SGR_VARIABLE_EXT}"

# Weight Wrapper: Emboldens or lightens outputs printed to the console. Weight can be specified using applicable arguments.
class Weight:
	# Bold Wrapper: Emboldens outputs printed to the console. Weight can be specified using applicable arguments.
	def BOLD():
		return f"{START_CODE_EXT}1{SGR_VARIABLE_EXT}"
	# Light Wrapper: Lightens outputs printed to the console. Weight can be specified using applicable arguments.
	def LIGHT():
		return f"{START_CODE_EXT}2{SGR_VARIABLE_EXT}"

# Line Wrapper: Underlines outputs printed to the console. Can be either over or under. It can also be used to remove the underline from links output to the console.
class Line:
	def OVER():
		return f"{START_CODE_EXT}53{SGR_VARIABLE_EXT}"
	def UNDER(amnt):
		if amnt == 1:
			return f"{START_CODE_EXT}4{SGR_VARIABLE_EXT}"
		if amnt == 2:
			return f"{START_CODE_EXT}21{SGR_VARIABLE_EXT}"
		else:
			return (
					print("There was an error underlining the text. Please set a value of either '1' or '2' when calling the underline function to define how many lines you would like."),
					exit(1)
			)
	def RM():
		return f"{START_CODE_EXT}24{SGR_VARIABLE_EXT}"

# Cross-out Wrapper: Cross-out strings printed to the console, as if marked for deletion.
def Cross():
	return f"{START_CODE_EXT}9{SGR_VARIABLE_EXT}"

# Frame Wrapper: Puts text in a box.
def Frame():
	return f"{START_CODE_EXT}51{SGR_VARIABLE_EXT}"

# Circle Wrapper: Encircles text.
def Circle():
	return f"{START_CODE_EXT}52{SGR_VARIABLE_EXT}"

# Blink Wrapper: Change the blink of the terminal's cursor, or just fully turn it off.
class Blink:
	def SLOW():
		return f"{START_CODE_EXT}5{SGR_VARIABLE_EXT}"
	def FAST():
		return f"{START_CODE_EXT}6{SGR_VARIABLE_EXT}"
	def OFF():
		return f"{START_CODE_EXT}25{SGR_VARIABLE_EXT}"


# BigX Wrappers: Combines two or more wrappers into a singular callable function for ease of use.
# Big2 Wrapper: Underlines and emboldens only.
def Big2(amount):
	amnt = amount
	return (
			Line.UNDER(amnt) +
			Weight.BOLD()
	)

# Big3 Wrapper: Italicizes, bolds, and underlines selected strings.
def Big3(amount):
	amnt = amount
	return (
			Line.UNDER(amnt) +
			Weight.BOLD() +
			Italic()
	)


# ------Others------

# Colorize Wrapper: Colorizes outputs printed to the console. Can colorize either the highlight (background behind the text) or the text itself.
class Colorize:
	def FONT(color):
		return f"{START_CODE_EXT}38;2;{color}"

	def HIGH(color):
		return f"{START_CODE_EXT}48;2;{color}"

	def FONT8(color_name, set_type = "main_colors"):
		try:
			code = COLOR_MAP[set_type][color_name]["fg"]
			return f"{START_CODE_EXT}{code}{SGR_VARIABLE_EXT}"
		except KeyError:
			raise ValueError(f"Color '{color_name}' not found in {set_type}")

	def HIGH8(color_name, set_type = "main_colors"):
		try:
			code = COLOR_MAP[set_type][color_name]["bg"]
			return f"{START_CODE_EXT}{code}{SGR_VARIABLE_EXT}"
		except KeyError:
			raise ValueError(f"Color '{color_name}' not found in {set_type}")
