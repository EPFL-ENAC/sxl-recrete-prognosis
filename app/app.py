import os

import bars_chart
import pie_chart

# from drawing import plot_drawing
import slab_drawing
import streamlit as st
from alias import alias
from PIL import Image
from process import processing

# Define page layout
st.set_page_config(layout="wide")

LOCAL_FOLDER_PATH = os.path.dirname(__file__)


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
    html_text(text=columns_title, color="#24acb2", font_size="22", text_align="center")

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

        if line == 4:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing = simulation_result[simulation_id][3]
                fig3 = pie_chart.plot(drawing)
                column.pyplot(fig3, use_container_width=True)
                fig3.clf()


def html_text(
    text: list, color: str = "#000000", font_size: str = "18", text_align: str = "left", column: bool = True
) -> None:
    """Generic function to create a row html text as cell content.

    Parameters
    ----------
    list_text : list or string
        list of the text to display in the columns
    color : str, optional
        Text color, by default "#000000"
    font_size : str, optional
        Text size, by default "18"
    text_align : str, optional
        Test alignment, by default "left"
    column : bool, optional
        If True, the text is displayed in 4 columns, by default True
    """

    if column:
        for i, column in enumerate(st.columns(4)):
            input_text = text[i]
            html_text = f'<p style="color:{color}; font-size: {font_size}px; text-align:{text_align};">{input_text}</p>'
            column.markdown(html_text, unsafe_allow_html=True)
    else:
        html_text = f'<p style="color:{color}; font-size: {font_size}px; text-align:{text_align};">{text}</p>'
        st.markdown(html_text, unsafe_allow_html=True)


def header():
    # html_path = os.path.join(LOCAL_FOLDER_PATH, "static", "header.html")
    # with open(html_path, "r") as f:
    #     html_content = f.read()
    # st.components.v1.html(html_content, width=None, height=300, scrolling=False)

    # st.components.v1.iframe("static/header.html", height=200, scrolling=False)

    with st.container():
        html_text(text="<b>APEC4 Flo:RE<b>", color="#010302", font_size="30", text_align="Left", column=False)
        html_text(
            text="Automated Pre-design and Embodied-carbon Calculator for floors made of REused cut concrete pieces",
            color="#1599d7",
            font_size="22",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""Flo:RE are new construction systems for floors made of reused cut
            concrete elements developped at EPFL. Depending on the the design project,
            Flo:RE solutions only reuse concrete cut from existing slabs or combine it
            with either new or reused steel profiles.""",
            font_size="18",
            text_align="Left",
            column=False,
        )
        image_path = os.path.join(LOCAL_FOLDER_PATH, "static", "slab_donor_2_new.png")

        if os.path.exists(image_path):
            st.image(Image.open(image_path))

        html_text(
            text="""
            APEC is an automated tool to Pre-design Flo:RE that match the specificities
            of your new design and of your concrete or steel donor structure.
            Enter your design and donor-structure specificities and APEC will
            suggest an adapted Flo:RE system and provides its embodied carbon.
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
            All the details of Flo:RE and APEC4 Flo:RE are available in this
            journal paper.
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            <i>APEC never replaces the work of a civil engineer and is only
            conceived an early pre-design stage supporting tool. <br>
            No composite action between concrete and steel is assumed. <br>
            Donor structures are assumed in good condition and designed based
            on Swiss standards at the time of constuction. <br>
            Concrete slabs are assumed to be flat, unprestressed,
            with unidirectional continuous reinforcement.</i>
            """,
            font_size="14",
            text_align="Left",
            column=False,
        )


def main_part():
    """This part contains the main part of the app (parameters selection and results display)"""
    st.markdown("#")
    st.markdown("#")

    col0, col1, col2, col3 = st.columns(4)
    columns_title = ["", "<b>Design 1</b>", "<b>Design 2</b>", "<b>Design 3</b>"]

    html_text(text=columns_title, color="#24acb2", font_size="22", text_align="center")

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


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    header()
    main_part()
