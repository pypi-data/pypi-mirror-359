# ModuShell

ModuShell is a Python package that makes it easy to style terminal output using clean, and readable wrappers. Whether you're coloring text, applying bold or italic effects, or combining multiple styles at once, ModuShell simplifies working with ANSI escape codes — no memorization needed.

![Version](https://img.shields.io/github/v/tag/irvingkennet45/ModuShell?label=version)
[![Latest Release](https://img.shields.io/github/v/tag/irvingkennet45/ModuShell.svg)](https://github.com/irvingkennet45/ModuShell/releases/latest)

![Last Commit](https://img.shields.io/github/last-commit/irvingkennet45/ModuShell)
[![License](https://img.shields.io/github/license/irvingkennet45/ModuShell.svg)](https://github.com/irvingkennet45/ModuShell/blob/main/LICENSE)

---

## ✨ Features ✨

### Text Styles 🖌️
Use classic font styling:
- _Italicize Outputs!_ (`Italic`)
- **Embolden Words!** (`Weight.BOLD`)
- Alternatively, Dim Statements! (`Weight.LIGHT`)
- Under or Overline! (`Line.OVER; Line.UNDER(amnt)`)
- Strike! You're ~~OUT~~! (`Cross`)

### Color Handling! 🎨
- Ability to specify foreground (`Colorize.FONT`) or background (`Colorize.HIGH`)
- 8-bit ANSI compatibility via `Colorize.FONT8` and `Colorize.HIGH8` with JSON-defined color tables

#### Supported Formats:
- RGB (`255, 255, 255`)
- HSL (`360, 0.99, 0.99`)
- Hexadecimal (`#FFFFFF` or `#ffffff`)

### Other Features 🔍
- Good for clean formating in `f-strings` and in printed outputs
- Comes with 2 preconfigured combinations (`Big2` & `Big3`)
---

## 🔗 Installation 🔗

_Currently manual install only, will be uploaded to PyPI soon, along with references._

---

## 🕵️‍♂️ Misc. Information 🕵️‍♂️

- Visit the `References.md` file for documentation