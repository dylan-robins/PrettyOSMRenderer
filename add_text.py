import argparse
import re
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from palette import Palette, load_colour_palettes

PALETTE_FILE = Path("base16_schemes.json")


def add_border(
    img: Image.Image,
    fill: str,
    border_size: int | tuple[int, int] | tuple[int, int, int, int],
) -> Image.Image:
    """
    Adds a border around the provided image

    Parameters
    ----------
    img : Image
        The image to add the border to.
    fill : str
        The colour of the border
    border_size : int | tuple[int, int] | tuple[int, int, int, int]
        The size of the border, in one of three formats:
        - int: uniform border around the image
        - tuple[int, int]: horizontal/vertical border sizes
        - tuple[int, int, int, int]: N/E/S/W border sizes
    """

    W, H = img.size
    if isinstance(border_size, int):
        desired_size = W + border_size * 2, H + border_size * 2

    elif len(border_size) == 2:
        hpad, vpad = border_size
        desired_size = W + vpad * 2, H + hpad * 2

    elif len(border_size) == 4:
        Npad, Epad, Spad, Wpad = border_size
        desired_size = W + Wpad + Epad, H + Npad + Spad
    else:
        raise ValueError(
            f"Invalid value {repr(border_size)} provided to argument border_size"
        )

    print(f"### Resizing image to {desired_size[0]}x{desired_size[1]} (fill: {fill})")

    new_im = Image.new("RGB", desired_size, fill)
    new_im.paste(
        img, ((desired_size[0] - W) // 2, (desired_size[1] - H) // 2,),
    )
    return new_im


def add_city_name(input_image: Path, output_image: Path, palette: Palette):

    print(f"### Loading image from {input_image}")
    img = Image.open(input_image)

    W, H = img.size
    print(f"### Loaded image of size {W}x{H}")

    # add a small border
    img = add_border(img, palette["base05"], 10)

    # portion of image width you want text width to be
    img_fraction = (W - 100) / W
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
    img = ImageOps.pad(img, desired_size, color=palette["base00"], centering=(0.5, 0),)

    W, H = img.size
    x, y = 0, H - text_H - 10
    print(f"### Rendering text at coordinates {x}x{y}")
    draw = ImageDraw.Draw(img)
    draw.text(
        xy=(x, y), text=text, fill=palette["base05"], font=font, align="center",
    )

    img = add_border(img, palette["base00"], 250)

    print(f"### Exporting image to {output_image}")
    img.save(output_image, optimize=True)

    preview_path = (
        output_image.parent / f"{output_image.stem}.small{output_image.suffix}"
    )
    print(f"### Exporting preview to {preview_path}")
    thumbnail = ImageOps.contain(img, (1920, 1920))
    thumbnail.save(preview_path, optimize=True)


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
