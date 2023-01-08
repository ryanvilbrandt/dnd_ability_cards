import importlib
import os.path
import tomllib
from glob import glob
from types import ModuleType
from typing import Any, List, Tuple

from PIL import Image

from pil_helpers import add_class_icon, save_page


def main():
    # from fighter import src
    # im = build_card("fighter", src, f"fighter/abilities/second_wind.toml")
    # im.show()

    # Normal-sized cards
    card_list = build_cards("fighter")
    card_list += build_cards("ranger")
    save_cards_to_pages(card_list)
    # Large monk pages
    card_list = build_cards("monk")
    save_cards_to_pages(card_list, (2, 2), "monk_pages")


def build_cards(class_name: str) -> List[Image]:
    # Load the class module
    class_module = importlib.import_module(f"{class_name}.src")
    # Build the cards defined by the given toml dicts
    images = []
    for toml_path in glob(f"{class_name}/abilities/*.toml"):
        filename = os.path.basename(toml_path).replace(".toml", ".png")
        print(filename)
        im = build_card(class_name, class_module, toml_path)
        # Save image file
        os.makedirs(f"output/{class_name}", exist_ok=True)
        im.save(f"output/{class_name}/{filename}")
        images.append(im)
    return images


def build_card(class_name: str, class_module: ModuleType, toml_path: str):
    # Load the given toml dict
    toml_dict = open_toml(toml_path)
    # Call class module code
    im = class_module.get_template(toml_dict)
    class_module.add_text(im, toml_dict)
    add_class_icon(im, class_name)
    return im


def open_toml(filepath: str) -> dict[str, Any]:
    with open(filepath, "rb") as f:
        return tomllib.load(f)


def gen_chunks(chunk_list, n):
    for i in range(0, len(chunk_list), n):
        yield chunk_list[i:i + n]


def save_cards_to_pages(card_list: List[Image], grid: Tuple[int, int] = (3, 3), folder: str = "pages"):
    os.makedirs(f"output/{folder}", exist_ok=True)
    for i, chunk in enumerate(gen_chunks(card_list, grid[0] * grid[1])):
        filename = f"output/{folder}/{i + 1:>03}.png"
        print(f"Saving {filename}")
        save_page(chunk, grid, filename, cut_line_width=10)


if __name__ == "__main__":
    main()
