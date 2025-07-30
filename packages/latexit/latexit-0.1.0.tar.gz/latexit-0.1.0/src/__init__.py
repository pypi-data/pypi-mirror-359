"""
latex_to_png: Render LaTeX code to PNG images with transparent background (no math mode required).
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image
import io
import matplotlib as mpl

mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'

def latexit(latex_code: str, output_path: str, dpi: int = 300, fontsize: int = 24, padding: int = 10):
    """
    Render LaTeX math code to a PNG image with a transparent background using matplotlib's mathtext engine.
    Only a subset of LaTeX math is supported (see matplotlib documentation).
    Args:
        latex_code (str): The LaTeX math code to render (no math mode required).
        output_path (str): Path to save the PNG image.
        dpi (int): Dots per inch for the output image.
        fontsize (int): Font size for the rendered text.
        padding (int): Padding around the rendered text in pixels.
    Raises:
        RuntimeError: If the LaTeX code cannot be rendered by mathtext.
    """
    # First pass: measure text size
    fig = plt.figure(figsize=(2, 2))
    fig.patch.set_alpha(0.0)
    try:
        text = fig.text(0, 0, f'${latex_code}$', fontsize=fontsize, color='black', va='bottom', ha='left')
        plt.axis('off')
        canvas = FigureCanvas(fig)
        canvas.draw()
        bbox = text.get_window_extent(renderer=canvas.get_renderer())
    except Exception as e:
        plt.close(fig)
        raise RuntimeError(f"Failed to render LaTeX with matplotlib's mathtext. Error: {e}\nNote: Only a subset of LaTeX math is supported. See https://matplotlib.org/stable/tutorials/text/mathtext.html")
    plt.close(fig)

    # Convert bbox from display units to inches
    width, height = bbox.width / dpi, bbox.height / dpi
    # Add padding in inches
    pad_inches = padding / dpi
    width += 2 * pad_inches
    height += 2 * pad_inches

    # Second pass: render tightly
    fig = plt.figure(figsize=(width, height))
    fig.patch.set_alpha(0.0)
    try:
        text = fig.text(pad_inches / width, pad_inches / height, f'${latex_code}$', fontsize=fontsize, color='black', va='bottom', ha='left')
        plt.axis('off')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        image = Image.open(buf)
        image.save(output_path)
    except Exception as e:
        plt.close(fig)
        raise RuntimeError(f"Failed to render LaTeX with matplotlib's mathtext. Error: {e}\nNote: Only a subset of LaTeX math is supported. See https://matplotlib.org/stable/tutorials/text/mathtext.html")
    plt.close(fig)

__all__ = ["latexit"] 