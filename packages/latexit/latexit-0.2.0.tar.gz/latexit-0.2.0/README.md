# latexit

Render LaTeX math formulas to PNG images from the command line, using pure Python and matplotlib's mathtext engine.

## Features
- **Pure Python**: No system LaTeX required, cross-platform.
- **CLI tool**: Convert LaTeX math snippets to PNG images.
- **Transparent background** and customizable DPI, font size, and padding.

## Limitations
- Only a subset of LaTeX math is supported (see [matplotlib mathtext documentation](https://matplotlib.org/stable/tutorials/text/mathtext.html)).
- The output may not look exactly like real LaTeX (TeX/Computer Modern), but you can get close by using the Computer Modern font (see below).

## Installation

### Option 1 Install via pip

   ```sh
   $ pip install latexit
   ```

### Option 2 Install manually
1. Clone the repository:
```sh
$ git clone https://github.com/yourusername/latexit.git
$ cd latexit
```
2. Install dependencies:
```sh
pip install -r requirements.txt
# or, if using pyproject.toml:
pip install .
```

## Usage

   ```sh
   latexit "\\frac{1}{2}" output.png
   ```

Options:
- `--dpi`: Set output DPI (default: 300)
- `--fontsize`: Set font size (default: 24)
- `--padding`: Set padding in pixels (default: 10)

## Example

```sh
latexit "x^2 + y^2 = z^2" pythagoras.png
```

## License
MIT

## Acknowledgments
This project was developed with guidance and code suggestions from an AI assistant Cursor (powered by OpenAI's GPT-4). 