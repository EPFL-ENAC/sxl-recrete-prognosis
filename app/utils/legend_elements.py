import os

import yaml
from PIL import Image, ImageDraw

LOCAL_FOLDER_PATH = os.path.dirname(__file__)


def html_to_rgb(html_color):
    # Convert HTML color code (e.g., "#RRGGBB") to RGB tuple
    return tuple(int(html_color[i : i + 2], 16) for i in (1, 3, 5))


def create_legend_icon(color, size):
    icon = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    draw.rectangle([(0, 0), size], fill=color)
    return icon


def save_icon_to_png(icon, filename):
    icon.save(filename, "PNG")


def load_color():
    yaml_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "app_layout_config.yml")
    markdown_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "static", "4.md")

    icon_width = 15
    icon_height = 10
    with open(yaml_filename) as yaml_file:
        color_data = yaml.safe_load(yaml_file)

    for entry in color_data["piechart_color"]:
        entry_name = list(entry.keys())[0]
        entry_color = list(entry.values())[0]
        icon_color = html_to_rgb(entry_color)
        icon_filename = os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "static", f"{entry_color}.png")

        legend_icon = create_legend_icon(icon_color, (icon_width, icon_height))
        save_icon_to_png(legend_icon, icon_filename)

        with open(markdown_filename, "a") as markdown_file:
            markdown_file.write(f"![{entry_name}]({icon_filename}) {entry_name}\n")


if __name__ == "__main__":
    load_color()
