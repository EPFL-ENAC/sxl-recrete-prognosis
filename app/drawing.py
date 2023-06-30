import plotly.graph_objects as go


def plot_drawing(l1: float, h: float, number_part: int = 1, beam_size: float = 0.1, beam_height: float = 0.5):
    fig = go.Figure()

    slab_x_dimension = l1 / (number_part)

    for i in range(number_part):
        offset_x = slab_x_dimension * i
        slab_y_dimension = h
        offset_y = -(h / 2)

        x_min = offset_x
        y_min = offset_y
        x_max = offset_x + slab_x_dimension
        y_max = offset_y + slab_y_dimension

        fig.add_shape(
            type="rect",
            x0=x_min,
            y0=y_min,
            x1=x_max,
            y1=y_max,
            line=dict(color="RoyalBlue"),
            fillcolor="lightskyblue",  # Transparent fill color
        )

    if number_part > 1:
        for i in range(number_part - 1):
            beam_center_x = slab_x_dimension * (i + 1)

            fig.add_shape(
                type="line",
                x0=beam_center_x - beam_size,
                y0=-(h / 2) - 0.25,
                x1=beam_center_x + beam_size,
                y1=-(h / 2) - 0.25,
                line=dict(color="black", width=3),
                label=dict(text=f"Beam size= {beam_size}"),
            )

            fig.add_trace(
                go.Scatter(
                    x=[beam_center_x],
                    y=[-(h / 2) - 0.2],
                    mode="text",
                    name="Lines and Text",
                    text=[f"Beam size= {beam_size}"],
                    textposition="top center",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[beam_center_x + 2 * beam_size],
                    y=[-(h / 2) - (beam_height)],
                    mode="text",
                    name="Lines and Text",
                    text=[f"Beam height= {beam_height}"],
                    textposition="top right",
                )
            )

            fig.add_shape(
                type="line",
                x0=beam_center_x,
                y0=-(h / 2) - 0.25 - (beam_height),
                x1=beam_center_x,
                y1=-(h / 2) - 0.25,
                line=dict(color="black", width=3),
                label=dict(text=f"Height = {beam_size}", padding=0),
            )

            fig.add_shape(
                type="line",
                x0=beam_center_x - beam_size,
                y0=-(h / 2) - 0.25 - beam_height,
                x1=beam_center_x + beam_size,
                y1=-(h / 2) - 0.25 - beam_height,
                line=dict(color="black", width=3),
            )

    # add L1 dimension
    fig.add_shape(
        type="line", x0=0, y0=2 * h, x1=l1, y1=2 * h, line=dict(color="RoyalBlue", width=3), label=dict(text=f"L1= {h}")
    )
    fig.add_shape(type="line", x0=0, y0=(2 * h) - 0.05, x1=0, y1=(2 * h) + 0.05, line=dict(color="RoyalBlue", width=3))
    fig.add_shape(
        type="line", x0=l1, y0=(2 * h) - 0.05, x1=l1, y1=(2 * h) + 0.05, line=dict(color="RoyalBlue", width=3)
    )

    fig.add_trace(
        go.Scatter(
            x=[l1 / 2],
            y=[(2 * h) + 0.1],
            mode="text",
            name="Markers and Text",
            text=[f"Slab length= {l1} m"],
            textposition="top center",
        )
    )

    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                x=l1 + 0.3,
                y=0,
                xref="x",
                yref="y",
                text=f"Slab height = {h} m",
                align="center",
                showarrow=False,
                yanchor="middle",
                textangle=90,
            )
        ]
    )

    # add H dimension
    fig.add_shape(
        type="line",
        x0=l1 + 0.1,
        y0=0 - (h / 2),
        x1=l1 + 0.1,
        y1=h / 2,
        line=dict(color="RoyalBlue", width=3),
        label=dict(text=f"H = {h}"),
    )

    fig.add_shape(
        type="line",
        x0=l1 + 0.1 - 0.025,
        y0=0 - (h / 2),
        x1=l1 + 0.1 + 0.025,
        y1=0 - (h / 2),
        line=dict(color="RoyalBlue", width=3),
    )

    fig.add_shape(
        type="line",
        x0=l1 + 0.1 - 0.025,
        y0=(h / 2),
        x1=l1 + 0.1 + 0.025,
        y1=(h / 2),
        line=dict(color="RoyalBlue", width=3),
    )

    fig.update_xaxes(range=[-0.2, l1 + 0.5], showgrid=False)
    # fig.update_yaxes(range=[-(2 * h + 1), (2 * h + 1)], showgrid=False)
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    fig.update_layout(showlegend=False)
    return fig


if __name__ == "__main__":
    plot_drawing(3, 0.5, 3).show()
