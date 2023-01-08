import os
from typing import Any

from PIL import Image

from enums import HAlign, VAlign
from pil_helpers import open_image, action_box, name_box, description_box, source_box, level_box, footnote_box, \
    TextBox, FONTS_FOLDER

small_description_box = TextBox(105, 150, 610, 700, font_size=23, halign=HAlign.LEFT, valign=VAlign.TOP,
                          font_name=os.path.join(FONTS_FOLDER, "Aktiv_Grotesque.otf"))


def get_template(toml_dict: dict[str, Any]) -> Image:
    action = toml_dict["action"].replace(" ", "_")
    filepath = f"templates/Template_{action}.png"
    return open_image(filepath)


def add_text(im: Image, toml_dict: dict[str, Any]):
    action_box.add_text(im, toml_dict["action"])
    name_box.add_text(im, toml_dict["name"])
    box = small_description_box if toml_dict["name"] == "Bladesong" else description_box
    box.add_text(im, toml_dict["description"])
    footnote_box.add_text(im, toml_dict["footnote"])
    source_box.add_text(im, toml_dict["source"])
    level_box.add_text(im, toml_dict["level"])
