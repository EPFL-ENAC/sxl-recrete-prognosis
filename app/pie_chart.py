import os

import matplotlib.pyplot as plt
import pandas as pd
import yaml

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "app_layout_config.yml")

with open(CONFIG_FILE_PATH) as f:
    config_file = yaml.safe_load(f)


def get_row_metadata(system_id, metadata_name):
    list_colors = []
    impact_reuse_matrix_row = config_file.get("impact_reuse_matrix_row")
    for i in impact_reuse_matrix_row:
        if i.get("system") == system_id:
            labels = i.get("labels")
            for label in labels:
                list_colors.append(label.get(metadata_name))
    return list_colors


def plot(df: pd.DataFrame, system_id):
    list_colors = get_row_metadata(system_id, "color")
    list_colors = [f"#{color}" for color in list_colors]

    total = sum(df["values"])
    percentages = [f"{round(value / total * 100, 1)}%" for value in df["values"]]

    # Create a pie chart
    fig, ax = plt.subplots()
    wedges, labels = ax.pie(df["values"], labels=percentages, colors=list_colors, autopct=None, startangle=90)

    return plt
