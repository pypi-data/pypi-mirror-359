import argparse
from . import latexit as _latexit
import sys
import os
import tempfile

def main():
    parser = argparse.ArgumentParser(description='Render LaTeX code to a PNG image with transparent background.')
    parser.add_argument('latex_code', type=str, help='The LaTeX code to render (no math mode required).')
    parser.add_argument('output_path', type=str, help='Path to save the PNG image.')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for the output image (default: 300).')
    parser.add_argument('--fontsize', type=int, default=24, help='Font size for the rendered text (default: 24).')
    parser.add_argument('--padding', type=int, default=10, help='Padding around the rendered text in pixels (default: 10).')
    args = parser.parse_args()
    try:
        _latexit(args.latex_code, args.output_path, dpi=args.dpi, fontsize=args.fontsize, padding=args.padding)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        # Try to print the LaTeX log file if available
        if 'TemporaryDirectory' in str(e):
            # Can't get log file path
            sys.exit(1)
        # Try to find the last used tempdir and log file
        # This is a best-effort: in most cases, the log is in the tempdir used by latexit
        # For debugging, suggest user to check their LaTeX installation
        print("\nIf this is a LaTeX error, please check your LaTeX installation (try running 'latex --version').", file=sys.stderr)
        sys.exit(1) 