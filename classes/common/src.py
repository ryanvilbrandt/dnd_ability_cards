from typing import Any

from PIL import Image

from pil_helpers import open_image, action_box, name_box, description_box, source_box, level_box, footnote_box

SCALE = 3/2  # 2x2 card grid rather than 3x3


def get_template(toml_dict: dict[str, Any]) -> Image.Image:
    action = toml_dict["action"].replace(" ", "_")
    filepath = f"templates/Template_{action}.png"
    im = open_image(filepath)
    width, height = im.size
    im = im.resize((int(SCALE * width), int(SCALE * height)))
    return im


def add_text(im: Image, toml_dict: dict[str, Any]):
    action_box.add_text(im, toml_dict["action"], scale=SCALE)
    name_box.add_text(im, toml_dict["name"], scale=SCALE)
    description_box.add_text(im, toml_dict["description"], scale=SCALE)
    if "footnote" in toml_dict:
        footnote_box.add_text(im, toml_dict["footnote"], scale=SCALE)
    source_box.add_text(im, toml_dict["source"], scale=SCALE)
    level_box.add_text(im, toml_dict["level"], scale=SCALE)
