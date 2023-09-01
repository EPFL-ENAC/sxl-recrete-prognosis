import os

import yaml
from PIL import Image, ImageDraw

LOCAL_FOLDER_PATH = os.path.dirname(__file__)


def html_to_rgb(value):
    red = int(value[1:3], 16)
    green = int(value[3:5], 16)
    blue = int(value[5:7], 16)

    # Convert HTML color code (e.g., "#RRGGBB") to RGB tuple
    return red, green, blue


def create_legend_icon(color, size):
    icon = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    draw.rectangle([(0, 0), size], fill=color)
    return icon


def save_icon_to_png(icon, filename):
    icon.save(filename, "PNG")


def load_color():
    yaml_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "app_layout_config.yml")
    markdown_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "static", "5.md")

    icon_width = 15
    icon_height = 10
    with open(yaml_filename) as yaml_file:
        color_data = yaml.safe_load(yaml_file)

    color_dict = {}

    impact_reuse_matrix_row = color_data.get("impact_reuse_matrix_row")
    for i in impact_reuse_matrix_row:
        i.get("system")
        labels = i.get("labels")
        for label in labels:
            color = label.get("color")
            name = label.get("name")
            color_dict[name] = color

    for name, color in color_dict.items():
        icon_color = html_to_rgb(str(color))
        icon_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "static", f"{color}.png")
        legend_icon = create_legend_icon(icon_color, (icon_width, icon_height))
        save_icon_to_png(legend_icon, icon_filename)

        with open(markdown_filename, "a") as markdown_file:
            markdown_file.write(f"![{name}]({icon_filename}) {name}\n")


if __name__ == "__main__":
    load_color()
