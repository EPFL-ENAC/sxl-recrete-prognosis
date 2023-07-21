import matplotlib.patches as patches
import matplotlib.pyplot as plt

DIMENSION_END_LINE_OFFSET = 0.02
DIMENSION_WIDTH = 2
SLAB_SEPARATION_LINE_WIDTH = 0.1
SLAB_LINE_DIMENSION_Y_OFFSET = 0.1
SLAB_TEXT_DIMENSION_Y_OFFSET = 0.2
SLAB_LINE_DIMENSION_X_OFFSET = 0.1
SLAB_TEXT_DIMENSION_X_OFFSET = 0.11
BEAM_VERTIAL_OFFSET = 0.1
BEAM_WIDTH = 3


def plot_drawing(l1: float, h: float, number_part: int = 1, beam_size: float = 0.1, beam_height: float = 0.5):
    # Create a figure and axis
    fig, ax = plt.subplots()

    slab_x_dimension = l1 / (number_part)
    slab_y_dimension = h

    # Draw slabs
    for i in range(number_part):
        slab_x_min = slab_x_dimension * i + (SLAB_SEPARATION_LINE_WIDTH * i)
        slab_y_min = -(h / 2)
        rect = patches.Rectangle(
            (slab_x_min, slab_y_min),
            slab_x_dimension,
            slab_y_dimension,
            linewidth=1,
            edgecolor="grey",
            fill=None,
            hatch="///",
        )
        ax.add_patch(rect)

    # Draw slab horizontal dimensions
    for i in range(number_part):
        slab_dim_x_min = slab_x_dimension * i + (SLAB_SEPARATION_LINE_WIDTH * i)
        slab_dim_x_max = slab_dim_x_min + slab_x_dimension
        slab_dim_y = (h / 2) + SLAB_LINE_DIMENSION_Y_OFFSET
        x = [slab_dim_x_min, slab_dim_x_max]
        y = [slab_dim_y, slab_dim_y]

        # lines
        ax.plot(x, y, color="black")

        # markers
        ax.plot(x, y, color="black", marker=(2, 0, 45), linestyle="None")
        ax.plot(x, y, color="black", marker=(2, 0, 0), linestyle="None")

        # text
        x = slab_dim_x_min + slab_x_dimension / 2
        y = (h / 2) + SLAB_TEXT_DIMENSION_Y_OFFSET
        ax.text(x, y, f"Slab length= {l1} m", fontsize=5, ha="center", va="center")

    # Draw slab vertical dimensions
    slab_dim_x = slab_dim_x_max + SLAB_LINE_DIMENSION_X_OFFSET
    slab_dim_y_min = -(h / 2)
    slab_dim_y_max = h / 2
    x = [slab_dim_x, slab_dim_x]
    y = [slab_dim_y_min, slab_dim_y_max]

    # lines
    ax.plot(x, y, color="black")

    # markers
    ax.plot(x, y, color="black", marker=(2, 0, 45), linestyle="None")
    ax.plot(x, y, color="black", marker=(2, 0, 90), linestyle="None")

    # text
    x = slab_dim_x + SLAB_TEXT_DIMENSION_X_OFFSET
    y = 0
    ax.text(x, y, f"Slab height= {h} m", fontsize=5, ha="center", va="center", rotation=90)

    # Draw beam
    if number_part > 1:
        for i in range(number_part - 1):
            beam_center_x = (
                slab_x_dimension * (i + 1) + (SLAB_SEPARATION_LINE_WIDTH * (i + 1)) - (SLAB_SEPARATION_LINE_WIDTH / 2)
            )
            beam_y_max = -(h / 2) - BEAM_VERTIAL_OFFSET
            x = [beam_center_x - beam_size, beam_center_x + beam_size]
            y = [beam_y_max, beam_y_max]
            ax.plot(x, y, color="grey", linewidth=BEAM_WIDTH)
            x = [beam_center_x, beam_center_x]
            y = [beam_y_max, beam_y_max - beam_height]
            ax.plot(x, y, color="grey", linewidth=BEAM_WIDTH)
            x = [beam_center_x - beam_size, beam_center_x + beam_size]
            y = [beam_y_max - beam_height, beam_y_max - beam_height]
            ax.plot(x, y, color="grey", linewidth=BEAM_WIDTH)

    # Set axis limits
    ax.set_xlim([-0.2, l1 + 0.5])
    ax.set_ylim([-2 * h - beam_height, +h * 2])

    # Set the aspect ratio
    ax.set_aspect("equal")

    # Remove frame border and ticks
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    return fig


if __name__ == "__main__":
    plot_drawing(3, 0.5, 3)
