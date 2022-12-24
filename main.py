import os.path
import tomllib
from glob import glob
from typing import Any

from PIL import Image

from monk.monk import get_monk_template, add_text
from pil_helpers import add_class_icon


def main():
    im = build_card(f"monk/abilities/ki.toml")
    im.show()
    # build_cards("monk")


def build_cards(dir_name: str):
    for filepath in glob(f"{dir_name}/abilities/*.toml"):
        filename = os.path.basename(filepath).replace(".toml", ".png")
        print(filename)
        build_card(filepath).save(f"output/{filename}")


def build_card(filepath: str):
    toml_dict = open_toml(filepath)
    im = get_monk_template(toml_dict)
    add_text(im, toml_dict)
    add_class_icon(im, "monk")
    return im


def open_toml(filepath: str) -> dict[str, Any]:
    with open(filepath, "rb") as f:
        return tomllib.load(f)


def build_page(card_list, grid_width, grid_height, filename, cut_line_width=3, page_ratio=8.5 / 11.0, h_margin=100):
    """
    Adds cards, in order, to a grid defined by grid_width, grid_height.
    It then adds a border to the grid, making sure to preserve the
    page ratio for later printing, and saves to filename
    Assumes that all the cards are the same size
    """
    # Create card grid based on size of the first card
    w, h = card_list[0].size
    bg = Image.new("RGB", (w * grid_width, h * grid_height))
    # Add cards to the grid, top down, left to right
    for y in range(grid_height):
        for x in range(grid_width):
            card = card_list.pop(0)
            coords = (x * (w + cut_line_width),
                      y * (h + cut_line_width))
            bg.paste(card, coords)
    # If there's a margin defined, add extra whitespace around the page
    # if h_margin > 0:
    #     w,h = bg.size
    #     w_margin = (((h_margin*2)+h)*page_ratio-w)/2.0
    #     w_margin = round(w_margin)
    #     page = Image.new("RGB", (int(w+w_margin*2), int(h+h_margin*2)), (255, 255, 255))
    #     page.paste(bg, (w_margin,h_margin))
    #     page.save(filename)
    # else:
    # bg.save(filename)
    # Create a paper image the exact size of an 8.5x11 paper
    # to paste the card images onto
    paper_width = int(8.5 * 300)  # 8.5 inches times 300 dpi
    paper_height = int(11 * 300)  # 11 inches times 300 dpi
    paper_image = Image.new("RGB", (paper_width, paper_height), (255, 255, 255))
    w, h = bg.size
    # TODO Add code that shrinks the bg if it's bigger than any dimension
    # of the Paper image
    paper_image.paste(bg, ((paper_width - w) / 2, (paper_height - h) / 2))
    paper_image.save(filename, dpi=(300, 300))


if __name__ == "__main__":
    main()
