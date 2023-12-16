import importlib
import os.path
import shutil
import tomllib
from glob import glob
from types import ModuleType
from typing import Any, List, Tuple, Optional

from PIL import Image

from pil_helpers import add_class_icon, save_page


def main(minimum_level: int = 1):
    # Normal-sized cards
    # card_list = build_cards("fighter", include_cards=[
    #     "monster_hunter_protection_from_evil_and_good",
    # ])
    # card_list = build_cards("fighter", minimum_level=minimum_level)
    # card_list += build_cards("ranger", minimum_level=minimum_level)
    # card_list += build_cards("wizard", minimum_level=minimum_level)
    # save_cards_to_pages(card_list)
    # Large monk pages
    card_list = build_cards("monk", minimum_level=minimum_level)
    save_cards_to_pages(card_list, (2, 2), "monk_pages")


def build_cards(class_name: str, minimum_level: int = 1, include_cards: List[str] = None) -> List[Image]:
    """
    Args:
        class_name:
        minimum_level:
        include_cards: If defined, only cards with filenames matching this value will be built.
            Does not include the file extension. e.g. superiority_dice
    """
    # Load the class module
    class_module = importlib.import_module(f"classes.{class_name}.src")
    # Build the cards defined by the given toml dicts
    images = []
    for toml_path in glob(f"classes/{class_name}/abilities/*.toml"):
        filename = os.path.basename(toml_path).replace(".toml", "")
        if include_cards and filename not in include_cards:
            continue
        im = build_card(class_name, class_module, toml_path, minimum_level=minimum_level)
        if im is None:
            continue
        # Save image file
        os.makedirs(f"output/cards/{class_name}", exist_ok=True)
        im.save(f"output/cards/{class_name}/{filename}.png")
        images.append(im)
    return images


def build_card(class_name: str, class_module: ModuleType, toml_path: str, minimum_level: int = 1) -> Optional[Image]:
    # Load the given toml dict
    toml_dict = open_toml(toml_path)
    if toml_dict.get("skip"):
        return None
    if int(toml_dict.get("level", 0)) < minimum_level:
        return None
    print(toml_dict["name"])
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
    folder_path = f"output/{folder}"
    shutil.rmtree(folder_path, ignore_errors=True)
    os.makedirs(folder_path, exist_ok=True)
    for i, chunk in enumerate(gen_chunks(card_list, grid[0] * grid[1])):
        filename = f"output/{folder}/{i + 1:>03}.png"
        print(f"Saving {filename}")
        save_page(chunk, grid, filename, cut_line_width=10)


if __name__ == "__main__":
    main(minimum_level=4)
