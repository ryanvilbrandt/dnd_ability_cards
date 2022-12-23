from typing import Any

from main import action_box, ki_box, name_box_w_ki, name_box, description_box, source_box, level_box, \
    DEBUG_TEXT_BOX_BORDERS


def get_monk_template(toml_dict: dict[str, Any]) -> Image:
    ki = "Ki_" if toml_dict["cost"] else ""
    action = toml_dict["action"].replace(" ", "_")
    return open_image(f"templates/Template_{ki}{action}.png")


def add_text(im: Image, toml_dict: dict[str, Any]):
    action_box.add_text(im, toml_dict["action"])
    if toml_dict["cost"]:
        ki_box.add_text(im, toml_dict["cost"])
        name_box_w_ki.add_text(im, toml_dict["name"])
    else:
        name_box.add_text(im, toml_dict["name"])
    print(toml_dict["description"])
    description_box.add_text(im, toml_dict["description"])
    source_box.add_text(im, toml_dict["source"])
    level_box.add_text(im, toml_dict["level"])

    if DEBUG_TEXT_BOX_BORDERS:
        action_box.draw_box(im)
        if toml_dict["cost"]:
            ki_box.draw_box(im)
            name_box_w_ki.draw_box(im)
        else:
            name_box.draw_box(im)
        description_box.draw_box(im)
        source_box.draw_box(im)
        level_box.draw_box(im)
