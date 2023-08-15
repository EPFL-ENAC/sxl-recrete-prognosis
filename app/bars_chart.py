import matplotlib.pyplot as plt
import pandas as pd

BAR_WIDTH = 0.5


def plot(df: pd.DataFrame):
    colors = ["#bfbfbf", "#24acb2"]
    labels = ["Conventional solution \n (new flat RC slab)", "Flo:RE solution \n (reused concrete)"]
    bars = plt.bar(labels, df["values"], color=colors, width=BAR_WIDTH)
    plt.ylabel("kgCO₂ eq/m²")
    # plt.title("Embodied carbon comparison")

    # Remove the border of the chart
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["bottom"].set_visible(False)
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(color="grey", alpha=0.2)

    # Remove the y-axis ticks
    plt.tick_params(left=False)

    # Set the background color to transparent
    plt.gcf().set_facecolor("none")

    # Make the plot and axis backgrounds transparent
    plt.gca().set_facecolor("none")

    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(round(bar.get_height())),
            ha="center",
            va="bottom",
            fontsize=14,
        )

    plt.plot([0.5 - BAR_WIDTH / 2, 0.5], [df["values"].iloc[0], df["values"].iloc[0]], color="black", lw=0.5)
    plt.plot([0.5 + BAR_WIDTH / 2, 0.5], [df["values"].iloc[1], df["values"].iloc[1]], color="black", lw=0.5)
    # Add the arrow
    plt.annotate(
        "",
        xy=(0.5, df["values"].iloc[1]),
        xytext=(0.5, df["values"].iloc[0]),
        arrowprops=dict(facecolor="black", arrowstyle="->", lw=0.5, mutation_scale=40),
    )

    reduction = round((1 - (df["values"].iloc[1] / df["values"].iloc[0])) * 100)

    x_text = 0.6
    y_text = df["values"].iloc[0] + (df["values"].iloc[1] - df["values"].iloc[0]) / 2
    plt.text(x_text, y_text, f"-{reduction}%", ha="center", va="center", rotation=0, fontsize=14)

    plt.tight_layout()

    return plt


if __name__ == "__main__":
    bar_char_data = pd.DataFrame({"labels": ["Impact new", "Impact reuse"], "values": [73.851594, 8.575929]})
    bar_char_data.set_index("labels", inplace=True)

    plot(bar_char_data).show()
