import os

import matplotlib.pyplot as plt
import pandas as pd
import yaml

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "app_layout_config.yml")

with open(CONFIG_FILE_PATH) as f:
    config_file = yaml.safe_load(f)
    config = {}
    for key, value in config_file.items():
        temp_dict = {}
        for i in value:
            for k, v in i.items():
                temp_dict[k] = v
        config[key] = temp_dict


def plot(df: pd.DataFrame):
    defaut_color = config.get("piechart_color").get("default")
    list_colors = [config.get("piechart_color").get(label, defaut_color) for label in df.index]
    list_colors = ["#" + color for color in list_colors]

    total = sum(df["values"])
    percentages = [f"{round(value / total * 100, 1)}%" for value in df["values"]]

    # Create a pie chart
    fig, ax = plt.subplots()
    wedges, labels = ax.pie(df["values"], labels=percentages, colors=list_colors, autopct=None, startangle=90)

    return plt


if __name__ == "__main__":
    bar_char_data = pd.DataFrame(
        {"labels": ["cut concrete transportation", "concrete sawing", "label3"], "values": [73.851594, 8.575929, 11]}
    )
    bar_char_data.set_index("labels", inplace=True)

    plot(bar_char_data).show()
