"""
Meet Symbolic, a converter that turns your images into braille-style ASCII art - right in your terminal.
PNG, JPG, JPEG, and WEBP -~ all supported!

How to use:
1. Please install the numpy and pillow modules.
2. When prompted, choose whether to open the folder and import your image.
3. Sit back while the image is converted and printed to your terminal.

That sums it up. Don't forget to enjoy the art. -Enjoy!~
"""

import argparse
import atexit
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import tkinter as tk
from tkinter import filedialog

SYMBOLS = np.array(list("⣿⣾⣷⣯⣤⣄⣀░▒▓█"))

_tk_root = None


def get_tk_root():
    """Return a shared, withdrawn Tk root, creating it on first use."""
    global _tk_root
    if _tk_root is None:
        _tk_root = tk.Tk()
        _tk_root.withdraw()
        atexit.register(_tk_root.destroy)
    return _tk_root


def safe_input(prompt_text):
    """Read a line from stdin, converting Ctrl+C and EOF into a clean exit."""
    try:
        return input(prompt_text)
    except (KeyboardInterrupt, EOFError):
        print("\n\nKeyboard interrupt detected. Exiting safely...\n")
        raise SystemExit(0)


def confirm(prompt_text):
    """Ask a yes/no confirmation, returning True only on 'y'."""
    while True:
        raw = safe_input(prompt_text).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no", "exit", "quit", "q"):
            return False
        print("Error: Please enter 'y' or 'n'.")


def copy_to_clipboard(text):
    """Copy the given text to the system clipboard, returning True on success."""
    try:
        root = get_tk_root()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        return True
    except Exception:
        return False


def select_image():
    """Open a file dialog and return the path of the chosen image, or an empty string."""
    try:
        root = get_tk_root()
        return filedialog.askopenfilename(
            parent=root,
            title="Select Image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
        )
    except Exception:
        return ""


def resize(img, width, compact):
    """Resize the image to the given width, scaling height by aspect ratio and compactness."""
    w, h = img.size
    aspect = h / w
    scale = 0.50 if compact else 0.70
    new_h = max(1, int(aspect * width * scale))
    return img.resize((width, new_h))


def enhance(img):
    """Boost contrast and sharpness, then apply edge enhancement."""
    img = ImageEnhance.Contrast(img).enhance(1.6)
    img = ImageEnhance.Sharpness(img).enhance(2.5)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img


def grayscale(img):
    """Convert the image to grayscale."""
    return img.convert("L")


def floyd_steinberg_dither(img_array):
    """Apply Floyd–Steinberg dithering to the grayscale array, quantized to the symbol levels."""
    arr = img_array.astype(float)
    h, w = arr.shape
    for y in range(h):
        for x in range(w):
            old = arr[y, x]
            new = round((old / 255) * (len(SYMBOLS) - 1)) * (255 / (len(SYMBOLS) - 1))
            arr[y, x] = new
            err = old - new
            if x + 1 < w:
                arr[y, x + 1] += err * 7 / 16
            if x - 1 >= 0 and y + 1 < h:
                arr[y + 1, x - 1] += err * 3 / 16
            if y + 1 < h:
                arr[y + 1, x] += err * 5 / 16
            if x + 1 < w and y + 1 < h:
                arr[y + 1, x + 1] += err * 1 / 16
    return np.clip(arr, 0, 255).astype(np.uint8)


def map_pixels(img):
    """Dither the image and map each pixel to a braille-style symbol."""
    pixels = np.array(img)
    pixels = floyd_steinberg_dither(pixels)
    scale = len(SYMBOLS) - 1
    gamma = 0.8
    chars = [
        SYMBOLS[int(((p / 255) ** gamma) * scale)]
        for p in pixels.flatten()
    ]
    return chars


def render(chars, width):
    """Join the symbol list into lines of the given width."""
    return "\n".join(
        "".join(chars[i:i + width])
        for i in range(0, len(chars), width)
    )


def convert(path, width, compact):
    """Load, resize, enhance, grayscale, dither, and render the image as a symbol string."""
    img = Image.open(path)
    img = resize(img, width, compact)
    img = enhance(img)
    img = grayscale(img)
    chars = map_pixels(img)
    return render(chars, img.width)


def main():
    """Run the interactive Symbolic converter."""
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", help="Image path")
    parser.add_argument("-w", "--width", type=int, default=60)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    print("\nWelcome to Symbolic - an image-to-braille art converter - supporting PNG, JPG, JPEG, and WEBP formats!\n")

    while True:
        if args.image:
            path = args.image
        else:
            if confirm("\nOpen your file manager and import an image? (y/n): "):
                path = select_image()
            else:
                path = ""
        if not path:
            print("No image selected.")
        else:
            result = convert(path, args.width, args.compact)
            print("\n")
            print(result)

            if confirm("\nCopy the art to your clipboard? (y/n): "):
                if copy_to_clipboard(result):
                    print("Copied to clipboard!")
                else:
                    print("Error: Could not copy the art to the clipboard.")

        if not confirm("\nConvert another image? (y/n): "):
            break
        args.image = None

    print("\nGoodbye!~ May the art~bring you joy!~\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nKeyboard interrupt detected. Exiting safely...\n")
