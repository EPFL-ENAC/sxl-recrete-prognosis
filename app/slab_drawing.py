import math

import matplotlib.patches as patches
import matplotlib.pyplot as plt

DIMENSION_END_LINE_OFFSET = 0.02
DIMENSION_WIDTH = 0.5
SLAB_SEPARATION_LINE_WIDTH = 0.1
SLAB_LINE_DIMENSION_Y_OFFSET = 0.25
SLAB_TEXT_DIMENSION_Y_OFFSET = 0.5
SLAB_LINE_DIMENSION_X_OFFSET = 0.1
SLAB_TEXT_DIMENSION_X_OFFSET = 0.11
TEXT_DIMENSION_SIZE = 10
BEAM_VERTIAL_OFFSET = 0.1
BEAM_WIDTH = 1
BEAM_MARKER_SIZE = 5


def plot_transverse_section(
    length: float, height: float, number_part: int = 1, beam_length: float = 0.0, beam_height: float = 0.0
) -> object:
    """Create a transversal section matplotlib plot

    Parameters
    ----------
    length : float
        length of the slab
    height : float
        height of the slab
    number_part : int, optional
        number of part of the slab to draw, by default 1
    beam_length : float, optional
        beam length, by default 0.0
    beam_height : float, optional
        beam heigth, by default 0.0

    Returns
    -------
    object
        Matplotlib plot
    """

    # Create a figure and axis
    fig, ax = plt.subplots()

    slab_x_dimension = length
    slab_y_dimension = height

    # Draw main slabs
    for i in range(number_part):
        slab_x_min = slab_x_dimension * i + (SLAB_SEPARATION_LINE_WIDTH * i)
        slab_y_min = -(height / 2)
        rect = patches.Rectangle(
            (slab_x_min, slab_y_min),
            slab_x_dimension,
            slab_y_dimension,
            linewidth=1,
            edgecolor="grey",
            facecolor="lightgrey",
            # hatch="///",
        )
        ax.add_patch(rect)

    # Draw left slide half slabs
    slab_x_min = 0 - (slab_x_dimension / 2) - SLAB_SEPARATION_LINE_WIDTH
    slab_y_min = -(height / 2)
    rect = patches.Rectangle(
        (slab_x_min, slab_y_min),
        slab_x_dimension / 2,
        slab_y_dimension,
        linewidth=1,
        edgecolor="grey",
        facecolor="lightgrey",
        # hatch="///",
    )
    ax.add_patch(rect)

    # Draw right slide half slabs
    slab_x_min = slab_x_dimension * number_part + (SLAB_SEPARATION_LINE_WIDTH * number_part)
    slab_y_min = -(height / 2)
    rect = patches.Rectangle(
        (slab_x_min, slab_y_min),
        slab_x_dimension / 2,
        slab_y_dimension,
        linewidth=1,
        edgecolor="grey",
        facecolor="lightgrey",
        # hatch="///",
    )
    ax.add_patch(rect)

    # Draw slab horizontal dimensions
    slab_id = math.ceil(number_part / 2) - 1
    slab_dim_x_min = slab_x_dimension * slab_id + (SLAB_SEPARATION_LINE_WIDTH * slab_id)
    slab_dim_x_max = slab_dim_x_min + slab_x_dimension
    slab_dim_y = (height / 2) + SLAB_LINE_DIMENSION_Y_OFFSET
    x = [slab_dim_x_min, slab_dim_x_max]
    y = [slab_dim_y, slab_dim_y]
    # lines
    ax.plot(x, y, linewidth=DIMENSION_WIDTH, color="black")
    # markers
    ax.plot(x, y, color="black", marker=(2, 0, -45), linestyle="None", linewidth=DIMENSION_WIDTH)
    ax.plot(x, y, color="black", marker=(2, 0, 0), linestyle="None", linewidth=DIMENSION_WIDTH)
    # text
    x = slab_dim_x_min + slab_x_dimension / 2
    y = (height / 2) + SLAB_TEXT_DIMENSION_Y_OFFSET
    text_length = round(length, 2)
    ax.text(x, y, f"cut-piece length : {text_length} m", fontsize=TEXT_DIMENSION_SIZE, ha="center", va="center")

    # Draw beam
    for i in range(number_part + 1):
        beam_center_x = slab_x_dimension * i + (SLAB_SEPARATION_LINE_WIDTH * i) - (SLAB_SEPARATION_LINE_WIDTH / 2)
        beam_y_max = -(height / 2) - BEAM_VERTIAL_OFFSET
        x = [beam_center_x - beam_length, beam_center_x + beam_length]
        y = [beam_y_max, beam_y_max]
        ax.plot(x, y, color="black", linewidth=BEAM_WIDTH)
        x = [beam_center_x, beam_center_x]
        y = [beam_y_max, beam_y_max - beam_height]
        ax.plot(x, y, color="black", linewidth=BEAM_WIDTH)
        x = [beam_center_x - beam_length, beam_center_x + beam_length]
        y = [beam_y_max - beam_height, beam_y_max - beam_height]
        ax.plot(x, y, color="black", linewidth=BEAM_WIDTH)

    # Set axis limits
    ax.set_xlim(
        [
            -slab_x_dimension / 2,
            0.5 * slab_x_dimension
            + slab_x_dimension * (number_part)
            + (SLAB_SEPARATION_LINE_WIDTH * (number_part + 1)),
        ]
    )
    ax.set_ylim([-2 * height - beam_height, height * 4])

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

    # Set the background color to red
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)

    return plt


def plot_longitudinal_section(length: float, height: float, number_part: int = 1, beam_height: float = 0.5) -> object:
    """Create a longitudinal section matplotlib plot

    Parameters
    ----------
    length : float
        Slab length
    height : float
        Slab height
    number_part : int, optional
        Number of slab to draw, by default 1
    beam_height : float, optional
        Beam heigth, by default 0.5

    Returns
    -------
    object
        Matplotlib plot
    """
    print("--------")

    with_beam = True if beam_height > 0 else False

    # Create a figure and axis
    fig, ax = plt.subplots()

    slab_x_dimension = length
    slab_y_dimension = height

    # Draw main slabs
    for i in range(number_part):
        slab_x_min = slab_x_dimension * i + (SLAB_SEPARATION_LINE_WIDTH * i)
        slab_y_min = 0
        rect = patches.Rectangle(
            (slab_x_min, slab_y_min),
            slab_x_dimension,
            slab_y_dimension,
            linewidth=1,
            edgecolor="grey",
            facecolor="lightgrey",
            # hatch="///",
        )
        ax.add_patch(rect)

    # Draw beam
    vertical_offset = 0
    if with_beam:
        beam_x_min = 0
        beam_y_min = -beam_height
        beam_x_dimension = (slab_x_dimension + SLAB_SEPARATION_LINE_WIDTH) * number_part - SLAB_SEPARATION_LINE_WIDTH
        beam_y_dimension = beam_height

        rect = patches.Rectangle(
            (beam_x_min, beam_y_min),
            beam_x_dimension,
            beam_y_dimension,
            linewidth=1,
            edgecolor="grey",
            facecolor="white",
            # hatch="///",
        )
        ax.add_patch(rect)
        vertical_offset = beam_y_min

    # Add marker
    beam_marker_y = vertical_offset - BEAM_MARKER_SIZE / 100
    slab_x_max = (slab_x_dimension + SLAB_SEPARATION_LINE_WIDTH) * number_part - SLAB_SEPARATION_LINE_WIDTH

    ax.plot(
        0,
        beam_marker_y,
        color="black",
        marker="^",
        markersize=BEAM_MARKER_SIZE,
        markerfacecolor="none",
        markeredgecolor="black",
    )
    ax.plot(
        slab_x_max,
        beam_marker_y,
        color="black",
        marker="^",
        markersize=BEAM_MARKER_SIZE,
        markerfacecolor="none",
        markeredgecolor="black",
    )

    # Draw beam horizontal dimensions
    x_min = 0
    x_max = slab_x_max
    y_max = -beam_height
    y_min = y_max - SLAB_LINE_DIMENSION_Y_OFFSET
    offset = slab_x_max / 75

    x = [x_min, x_min]
    y = [y_min - offset, y_max]
    ax.plot(x, y, color="black", linewidth=DIMENSION_WIDTH)

    x = [x_max, x_max]
    y = [y_min - offset, y_max]
    ax.plot(x, y, color="black", linewidth=DIMENSION_WIDTH)

    x = [x_min - offset, x_max + offset]
    y = [y_min, y_min]
    ax.plot(x, y, color="black", linewidth=DIMENSION_WIDTH)

    ax.plot(x_min, y_min, color="black", marker=(2, 0, -45), linestyle="None")
    ax.plot(x_max, y_min, color="black", marker=(2, 0, -45), linestyle="None")

    # Draw slab horizontal dimensions
    slab_id = math.ceil(number_part / 2) - 1
    slab_dim_x_min = slab_x_dimension * slab_id + (SLAB_SEPARATION_LINE_WIDTH * slab_id)

    x = slab_x_max / 2
    y = y_min - slab_x_max / 40
    text_length = round(length * number_part, 2)
    ax.text(x, y, f"new design span :  {text_length} m", fontsize=TEXT_DIMENSION_SIZE, ha="center", va="center")

    slab_dim_x_max = slab_dim_x_min + slab_x_dimension
    slab_dim_y = (height / 2) + SLAB_LINE_DIMENSION_Y_OFFSET
    x = [slab_dim_x_min, slab_dim_x_max]
    y = [slab_dim_y, slab_dim_y]
    # lines
    ax.plot(x, y, color="black", linewidth=DIMENSION_WIDTH)
    # markers
    ax.plot(x, y, color="black", marker=(2, 0, -45), linestyle="None")
    ax.plot(x, y, color="black", marker=(2, 0, 0), linestyle="None")
    # text
    x = slab_dim_x_min + slab_x_dimension / 2
    y = slab_dim_y + (slab_x_max / 40)
    text_length = round(length, 2)
    ax.text(x, y, f"cut-piece width: {text_length} m", fontsize=TEXT_DIMENSION_SIZE, ha="center", va="center")

    # Set axis limits
    ax.set_xlim(
        [
            -0.1,
            0.1 + slab_x_dimension * (number_part) + (SLAB_SEPARATION_LINE_WIDTH * (number_part + 1)),
        ]
    )
    ax.set_ylim([-6 * height - beam_height, height * 4])

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

    # Set the background color to red
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)

    return plt


if __name__ == "__main__":
    # plot_transverse_section(
    #     length=3,
    #     height=0.3,
    #     number_part=1,
    #     beam_length=0.1,
    #     beam_height=0.2,
    # ).show()

    plot_longitudinal_section(
        length=1.5,
        height=0.14,
        number_part=2,
        beam_height=0,
    ).show()
