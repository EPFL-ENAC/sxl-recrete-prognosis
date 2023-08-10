import os

import bars_chart

# from drawing import plot_drawing
import slab_drawing
import streamlit as st
from alias import alias
from process import processing

# Define page layout
st.set_page_config(layout="wide")


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title("Reused as-cut cast-in-place concrete slab pieces")


def selectbox_input(
    parameter_name: str, parmater_description: str, options: tuple, result: list, index: int = 0, on_change=None
):
    """Generic function to create a row of 4 columns and add select boxes as cell content.
    Save the chosen parameter under the result list

    Parameters
    ----------
    parameter_name : str
        Name of the parameter. Uses as key for the simulation dictionary in the result list.
    parmater_description : str
        Description of the parameter to desplay in the first column
    options : tuple
        Tuple of the options to display in the select box
    result : list
        List of dictionaries containing the chosen parameters, with one dictionary per simulation.
    """
    for i, column in enumerate(st.columns(4)):
        if i == 0:
            column.write(parmater_description)
        else:
            with column:
                res = column.selectbox(
                    label=f"{parmater_description}{i}",
                    options=options,
                    label_visibility="collapsed",
                    index=index,
                    on_change=on_change,
                )
                if alias.get(parameter_name):
                    result[i - 1][parameter_name] = alias.get(parameter_name).get(res)
                else:
                    result[i - 1][parameter_name] = res


def number_input(
    parameter_name: str,
    parmater_description: str,
    min_value: float,
    max_value: float,
    default_value: float,
    step: float,
    result: list,
    disabled: list = [False, False, False],
):
    """Generic function to create a row of 4 columns and add input numbers as cell content.
    Save the chosen parameter under the result list

    Parameters
    ----------
    parameter_name : str
        Name of the parameter. Uses as key for the simulation dictionary in the result list.
    parmater_description : str
        Description of the parameter to desplay in the first column
    min_value : float
        Min value of the parameter
    max_value : float
        Max value of the parameter
    default_value : float
        Default value of the parameter
    step : float
        Step of the parameter
    result : list
        List of dictionaries containing the chosen parameters, with one dictionary per simulation.
    """
    for i, column in enumerate(st.columns(4)):
        if i == 0:
            column.write(parmater_description)
        else:
            with column:
                res = column.number_input(
                    label=f"{parmater_description}{i}",
                    min_value=min_value,
                    max_value=max_value,
                    value=default_value,
                    step=step,
                    label_visibility="collapsed",
                    disabled=disabled[i - 1],
                )
                result[i - 1][parameter_name] = res


def run_simulation(result: list):
    """This function takes the input parameters, run the simulation and display the results.

    Parameters
    ----------
    result : list
        List of the input parameters.
    """
    simulation_result = []
    for simulation_id, simulation_params in enumerate(result):
        simulation_result.append(processing(**simulation_params))

    # Add columns titles
    col0, col1, col2, col3 = st.columns(4)
    columns_title = ["", "<b>Design 1</b>", "<b>Design 2</b>", "<b>Design 3</b>"]
    html_text(list_text=columns_title, color="#24acb2", font_size="22", text_align="center")

    # Iterate over the 5 lines of the results
    for line in range(5):
        # st.markdown("---")
        col0, col1, col2, col3 = st.columns(4)

        path_description = os.path.join(os.path.dirname(__file__), "description", f"{line}.md")

        with open(path_description) as f:
            markdown_text = f.read()
        col0.markdown(markdown_text)

        if line == 0:
            for simulation_id, column in enumerate([col1, col2, col3]):
                column.write(f"The selected system is : {simulation_result[simulation_id][0]}")

        if line == 1:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing = simulation_result[simulation_id][1]
                fig1 = slab_drawing.plot_transverse_section(
                    length=drawing.get("l0"),
                    height=drawing.get("h"),
                    number_part=drawing.get("number_part"),
                    beam_length=drawing.get("h"),
                    beam_height=drawing.get("h"),
                )
                column.pyplot(fig1, use_container_width=True)
                fig1.clf()

        if line == 2:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing = simulation_result[simulation_id][1]
                fig1 = slab_drawing.plot_longitudinal_section(
                    length=drawing.get("l1"),
                    height=drawing.get("h"),
                    number_part=drawing.get("number_part"),
                    beam_height=drawing.get("h"),
                )
                column.pyplot(fig1, use_container_width=True)
                fig1.clf()

        if line == 3:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing = simulation_result[simulation_id][2]
                fig2 = bars_chart.plot(drawing)
                column.pyplot(fig2, use_container_width=True)
                fig2.clf()

                # print(simulation_result[simulation_id][2])
                # fig = px.bar(
                #     simulation_result[simulation_id][2],
                #     y="values",
                #     labels={"values": "KgC0₂ eq/m³ emissions"},
                #     color_discrete_sequence=["grey"],
                #     text="values",
                # )
                # fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                # fig.update_layout(
                #     xaxis_title="",
                #     plot_bgcolor="rgba(0,0,0,0)",
                #     paper_bgcolor="rgba(0,0,0,0)",
                #     title="Embodied carbon comparison",
                # )

                # gap_betwwen_bars = 0.5

                # fig.update_layout(bargap=gap_betwwen_bars)

                # fig.add_shape(
                #     type="line",
                #     x0=0.5,
                #     y0=simulation_result[simulation_id][2]["values"].iloc[0],
                #     x1=0.5,
                #     y1=simulation_result[simulation_id][2]["values"].iloc[1],
                #     line=dict(
                #         color="black",
                #         width=1,

                #     ),
                # )

                # fig.add_shape(
                #     type="line",
                #     x0=0.5-(gap_betwwen_bars/2),
                #     y0=simulation_result[simulation_id][2]["values"].iloc[0],
                #     x1=0.5,
                #     y1=simulation_result[simulation_id][2]["values"].iloc[0],
                #     line=dict(
                #         color="black",
                #         width=1
                #     ),
                # )

                # fig.add_shape(
                #     type="line",
                #     x0=0.5+(gap_betwwen_bars/2),
                #     y0=simulation_result[simulation_id][2]["values"].iloc[1],
                #     x1=0.5,
                #     y1=simulation_result[simulation_id][2]["values"].iloc[1],
                #     line=dict(
                #         color="black",
                #         width=1
                #     ),
                # )

                # column.plotly_chart(fig, use_container_width=True)

        # if line == 2:
        #     for simulation_id, column in enumerate([col1, col2, col3]):
        #         fig = px.pie(
        #             simulation_result[simulation_id][2],
        #             values="values",
        #             names=simulation_result[simulation_id][2].index,
        #         )
        #         column.plotly_chart(fig, use_container_width=True)

        # if line == 3:
        #     for simulation_id, column in enumerate([col1, col2, col3]):
        #         fig = px.pie(
        #             simulation_result[simulation_id][3],
        #             values="values",
        #             names=simulation_result[simulation_id][3].index,
        #         )
        #         column.plotly_chart(fig, use_container_width=True)


def html_text(list_text: list, color: str = "#000000", font_size: str = "18", text_align: str = "left") -> None:
    """Generic function to create a row of 4 columns and add html text as cell content.

    Parameters
    ----------
    list_text : list
        list of the text to display in the columns
    color : str, optional
        Text color, by default "#000000"
    font_size : str, optional
        Text size, by default "18"
    text_align : str, optional
        Test alignment, by default "left"
    """
    for i, column in enumerate(st.columns(4)):
        text = list_text[i]
        html_text = f'<p style="color:{color}; font-size: {font_size}px; text-align:{text_align};">{text}</p>'
        column.markdown(html_text, unsafe_allow_html=True)


def main_part():
    st.markdown("#")
    st.markdown("#")

    col0, col1, col2, col3 = st.columns(4)
    columns_title = ["", "<b>Design 1</b>", "<b>Design 2</b>", "<b>Design 3</b>"]

    html_text(list_text=columns_title, color="#24acb2", font_size="22", text_align="center")

    # original_title = '<p style="color:#24acb2; font-size: 18px; text-align:center;"><b>Design 1</b></p>'
    # col1.markdown(original_title, unsafe_allow_html=True)
    # col1.write("**:#24acb2[Design 1]**")

    result = [{} for i in range(3)]

    html_text(
        ["", "<i>Step 1</i> <b>New design</b>", "<i>Step 1</i> <b>New design</b>", "<i>Step 1</i> <b>New design</b>"],
        font_size="18",
        text_align="center",
    )

    selectbox_input(
        parameter_name="q1",
        parmater_description="Use",
        options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
        result=result,
    )

    number_input(
        parameter_name="l1",
        parmater_description="Floor span [m]",
        min_value=2.0,
        max_value=8.0,
        default_value=6.0,
        step=0.5,
        result=result,
    )

    html_text(
        [
            "",
            "<i>Step 2</i> <b>Concrete donor structure</b>",
            "<i>Step 2</i> <b>Concrete donor structure</b>",
            "<i>Step 2</i> <b>Concrete donor structure</b>",
        ],
        font_size="18",
        text_align="center",
    )

    selectbox_input(
        parameter_name="q0",
        parmater_description="Original use",
        options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
        result=result,
    )

    selectbox_input(
        parameter_name="year",
        parmater_description="Construction period (design steel yield strength)",
        options=("1956-1967 (300 N/mm²)", "1968-1988 (390 N/mm²)", "1988-2023 (435 N/mm²)"),
        index=1,
        result=result,
    )

    number_input(
        parameter_name="l0",
        parmater_description="Slab span [m]",
        min_value=2.0,
        max_value=8.0,
        default_value=3.0,
        step=0.1,
        result=result,
    )

    number_input(
        parameter_name="hsreuse",
        parmater_description="Slab thickness [cm]",
        min_value=0.14,
        max_value=0.30,
        default_value=0.14,
        step=0.02,
        result=result,
    )

    number_input(
        parameter_name="tpdist_beton_reuse",
        parmater_description="Transportation distance the new design [km]",
        min_value=0,
        max_value=1000,
        default_value=20,
        step=5,
        result=result,
    )

    html_text(
        [
            "",
            "<i>Step 3</i> <b>Steal profiles</b>",
            "<i>Step 3</i> <b>Steal profiles</b>",
            "<i>Step 3</i> <b>Steal profiles</b>",
        ],
        font_size="18",
        text_align="center",
    )

    def with_steel_profil_distance():
        pass
        # print(result[0])

    selectbox_input(
        parameter_name="steel_profiles",
        parmater_description="Type of steel profiles",
        options=("Reused steel profiles", "New steel profile"),
        index=1,
        result=result,
        on_change=with_steel_profil_distance(),
    )

    tpdist_metal_reuse_disabled = [
        True if result[i].get("steel_profiles") == "New steel profile" else False for i in range(0, 3)
    ]

    number_input(
        parameter_name="tpdist_metal_reuse",
        parmater_description="Steel profiles [km]",
        min_value=0,
        max_value=1000,
        default_value=80,
        step=1,
        result=result,
        disabled=tpdist_metal_reuse_disabled,
    )

    st.markdown("#")

    with st.container():
        button_pressed = st.button("Run Simulations", use_container_width=True)
        st.markdown("#")

    if button_pressed:
        run_simulation(result=result)


if __name__ == "__main__":
    main_part()
