from typing import Any

from PIL import Image

from pil_helpers import open_image, action_box, name_box, description_box, source_box, level_box, footnote_box


def get_template(toml_dict: dict[str, Any]) -> Image:
    action = toml_dict["action"].replace(" ", "_")
    filepath = f"templates/Template_{action}.png"
    return open_image(filepath)


def add_text(im: Image, toml_dict: dict[str, Any]):
    action_box.add_text(im, toml_dict["action"])
    name_box.add_text(im, toml_dict["name"])
    description_box.add_text(im, toml_dict["description"])
    if "footnote" in toml_dict:
        footnote_box.add_text(im, toml_dict["footnote"])
    source_box.add_text(im, toml_dict["source"])
    level_box.add_text(im, toml_dict["level"])
