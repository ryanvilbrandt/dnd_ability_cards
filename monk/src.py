import os.path
from typing import Any

from PIL import Image

from pil_helpers import open_image, TextBox, action_box, name_box, description_box, source_box, level_box, footnote_box

DEBUG_TEXT_BOX_BORDERS = False


ki_box = TextBox(98, 46, 82, 82)
name_box_w_ki = TextBox(206, 46, 517, 82)


def get_template(toml_dict: dict[str, Any]) -> Image:
    ki = "Ki_" if toml_dict["cost"] else ""
    action = toml_dict["action"].replace(" ", "_")
    filepath = f"templates/Template_{ki}{action}.png"
    if not os.path.isfile(filepath):
        filepath = "monk/" + filepath
    return open_image(filepath)


def add_text(im: Image, toml_dict: dict[str, Any]):
    action_box.add_text(im, toml_dict["action"])
    if toml_dict["cost"]:
        ki_box.add_text(im, toml_dict["cost"])
        name_box_w_ki.add_text(im, toml_dict["name"])
    else:
        name_box.add_text(im, toml_dict["name"])
    description_box.add_text(im, toml_dict["description"])
    footnote_box.add_text(im, toml_dict["footnote"])
    source_box.add_text(im, toml_dict["source"])
    level_box.add_text(im, toml_dict["level"])
