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

    # Create a pie chart
    fig, ax = plt.subplots()
    wedges, labels, autopct = ax.pie(
        df["values"], labels=df.index, colors=list_colors, autopct="%1.1f%%", startangle=90
    )

    # Add a title
    ax.set_title("Embodied carbon distribution")

    # bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0)
    # kw = dict(arrowprops=dict(arrowstyle="-"),
    #         bbox=bbox_props, zorder=0, va="center")

    # for i, p in enumerate(wedges):
    #     ang = (p.theta2 - p.theta1)/2. + p.theta1
    #     y = np.sin(np.deg2rad(ang))
    #     x = np.cos(np.deg2rad(ang))
    #     horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    #     connectionstyle = f"angle,angleA=0,angleB={ang}"
    #     kw["arrowprops"].update({"connectionstyle": connectionstyle})
    #     ax.annotate(df.index[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
    #                 horizontalalignment=horizontalalignment, **kw)

    return plt


if __name__ == "__main__":
    bar_char_data = pd.DataFrame(
        {"labels": ["cut concrete transportation", "concrete sawing", "label3"], "values": [73.851594, 8.575929, 11]}
    )
    bar_char_data.set_index("labels", inplace=True)

    plot(bar_char_data).show()
