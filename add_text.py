import argparse
import re
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from palette import Palette, load_colour_palettes

PALETTE_FILE = Path("base16_schemes.json")


def add_city_name(input_image: Path, output_image: Path, palette: Palette):
    print(f"### Loading image from {input_image}")
    img = Image.open(input_image)

    W, H = img.size
    print(f"### Loaded image of size {W}x{H}")

    # portion of image width you want text width to be
    img_fraction = (W - 20) / W
    fontsize = 72
    text = "GRENOBLE"
    font = ImageFont.truetype("fonts/Raleway.ttf", fontsize)
    while font.getsize(text)[0] < img_fraction * img.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 10
        font = ImageFont.truetype("fonts/Raleway.ttf", fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 10
    font = ImageFont.truetype("fonts/Raleway.ttf", fontsize)
    text_W, text_H = font.getsize(text)
    print(f"### Calculated optimal font size: {fontsize} ({text_W}x{text_H})")

    desired_size = W + 0, H + text_H
    print(f"### Resizing image to {desired_size[0]}x{desired_size[1]}")
    img = ImageOps.pad(
        img,
        desired_size,
        color=palette["base00"],
        centering=(0.5, 0),
    )

    W, H = img.size
    x, y = 0, H - text_H - 10
    print(f"### Rendering text at coordinates {x}x{y}")
    draw = ImageDraw.Draw(img)
    draw.text(
        xy=(x, y),
        text=text,
        fill=palette["base05"],
        font=font,
        align="center",
    )

    desired_size = ceil(W*1.5), ceil(H*1.5)
    print(f"### Resizing image to {desired_size[0]}x{desired_size[1]}")
    img = ImageOps.pad(
        img,
        desired_size,
        color=palette["base02"],
        centering=(0.5, 0.5),
    )

    print(f"### Exporting image to {output_image}")
    img.save(output_image, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image",
        type=Path,
        nargs="+",
        help="Path to the images to process",
        required=True,
    )
    parser.add_argument(
        "--palette_file",
        type=Path,
        help="Path to a json file containing colour palettes",
        default=Path("base16_schemes.json"),
    )
    parser.add_argument(
        "--palette",
        type=str,
        help="Names of the palette to load from the palette_file",
        default="onedark",
    )
    parser.add_argument(
        "--export_dir",
        type=Path,
        help="Path to a directory in which to place the generated maps",
        default=Path("export"),
    )
    args = parser.parse_args()

    palettes = load_colour_palettes(args.palette_file)
    for image in args.image:
        add_city_name(
            image, args.export_dir / f"{image.stem}_edited.png", palettes[args.palette]
        )
