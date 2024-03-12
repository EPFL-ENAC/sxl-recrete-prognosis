import math
import os

import bars_chart
import pie_chart

# from drawing import plot_drawing
import slab_drawing
import streamlit as st
import yaml
from style import css
from about import about_section
from alias import alias
from conact import contact_section
from paper import paper_section
from PIL import Image
from process import processing
from utils.add_html import html_text

# Define page layout
st.set_page_config(
    page_title="Flo:RE Calculator",
    layout="wide"
)


LOCAL_FOLDER_PATH = os.path.dirname(__file__)


with open(os.path.join(LOCAL_FOLDER_PATH, "app_layout_config.yml")) as f:
    config = yaml.safe_load(f)

PAGE_THEME_COLOR = f"#{config.get('page_color')}"

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


def run_simulation(input_parameters: list) -> list:
    """This function takes the input parameters, run the simulation and display the results.

    Parameters
    ----------
    result : list
        List of the input parameters.

    Returns
    -------
    list
        List of the results of the simulation.
    """
    simulation_result = []
    for simulation_id, simulation_params in enumerate(input_parameters):
        simulation_result.append(processing(**simulation_params))

    return simulation_result


def display_results(simulation_result: list) -> None:
    """This function display the results of the simulation.

    Parameters
    ----------
    simulation_result : list
        List of the results of the simulation.
    """

    print(simulation_result)

    # Add columns titles
    col0, col1, col2, col3 = st.columns(4)
    columns_title = ["", "<b>Design 1</b>", "<b>Design 2</b>", "<b>Design 3</b>"]
    html_text(text=columns_title, color=PAGE_THEME_COLOR, font_size="22", text_align="center")

    # Iterate over the 5 lines of the results
    for line in range(6):
        # st.markdown("---")
        col0, col1, col2, col3 = st.columns(4)

        path_description = os.path.join(os.path.dirname(__file__), "static", f"{line}.md")

        with open(path_description) as f:
            markdown_text = f.read()
        col0.markdown(markdown_text)
        if line == 5:
            image_path = os.path.join(os.path.dirname(__file__), "static", "legend.png")
            image = Image.open(image_path)
            col0.image(image)

        if line == 0:
            for simulation_id, column in enumerate([col1, col2, col3]):
                column.write(simulation_result[simulation_id][0])

        if line == 1:
            for simulation_id, column in enumerate([col1, col2, col3]):
                system_id = simulation_result[simulation_id][-1]
                drawing_parameters = simulation_result[simulation_id][1]

                number_part = drawing_parameters.get("number_part")

                if system_id == 1:
                    beam_height = 0
                    length = drawing_parameters.get("l1") / 2 # FIXME is this correct?
                else:
                    beam_height = drawing_parameters.get("h")
                    length = drawing_parameters.get("l0")

                fig1 = slab_drawing.plot_transverse_section(
                    length=length,
                    height=drawing_parameters.get("h"),
                    number_part=number_part,
                    beam_length=beam_height,
                    beam_height=beam_height,
                    system_id=system_id,
                )
                column.pyplot(fig1, use_container_width=True)
                fig1.clf()

        if line == 2:
            for simulation_id, column in enumerate([col1, col2, col3]):
                system_id = simulation_result[simulation_id][-1]
                drawing_parameters = simulation_result[simulation_id][1]

                number_part = math.ceil(drawing_parameters.get("l1") / 2.5)

                if system_id == 1:
                    beam_height = 0
                    number_part = 1
                    length = drawing_parameters.get("l1")
                else:
                    beam_height = drawing_parameters.get("h")
                    length = drawing_parameters.get("l1") / number_part

                fig1 = slab_drawing.plot_longitudinal_section(
                    length=length,
                    height=drawing_parameters.get("h"),
                    number_part=number_part,
                    beam_height=beam_height,
                    system_id=system_id,
                )
                column.pyplot(fig1, use_container_width=True)
                fig1.clf()

        if line == 3:
            for simulation_id, column in enumerate([col1, col2, col3]):
                system_id = simulation_result[simulation_id][-1]
                if system_id == 1:
                    image_name = "slabs_without_beams.jpg"
                else:
                    image_name = "slabs_with_beams.jpg"

                image_path = os.path.join(os.path.dirname(__file__), "static", image_name)
                column.image(Image.open(image_path))

        if line == 4:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing_parameters = simulation_result[simulation_id][2]
                fig2 = bars_chart.plot(drawing_parameters)
                column.pyplot(fig2, use_container_width=True)
                fig2.clf()

        if line == 5:
            for simulation_id, column in enumerate([col1, col2, col3]):
                system_id = simulation_result[simulation_id][-1]
                drawing_parameters = simulation_result[simulation_id][3]
                os.path.join(os.path.dirname(LOCAL_FOLDER_PATH), "app", "app_layout_config.yml")
                # with open(yaml_filename, 'r') as yaml_file:
                #     color_data = yaml.safe_load(yaml_file)
                #     label_name = []
                #     for i in color_data['piechart_color']:
                #         label_name.append(list(i.keys())[0])

                # drawing_parameters = drawing_parameters.set_index(pd.Index(label_name))

                fig3 = pie_chart.plot(drawing_parameters, system_id)
                column.pyplot(fig3, use_container_width=True)
                fig3.clf()


def main_part():
    """This part contains the main part of the app (parameters selection and results display)"""

    st.write("<div class='mobile'>Mobile screen not supported</div>",unsafe_allow_html=True)
    
    col0, col1, col2, col3 = st.columns(4)
    columns_title = ["", "<b>Design 1</b>", "<b>Design 2</b>", "<b>Design 3</b>"]

    html_text(text=columns_title, color=PAGE_THEME_COLOR, font_size="22", text_align="center")

    # original_title = '<p style="color:#24acb2; font-size: 18px; text-align:center;"><b>Design 1</b></p>'
    # col1.markdown(original_title, unsafe_allow_html=True)
    # col1.write("**:#24acb2[Design 1]**")

    input_paramters = [{} for i in range(3)]

    html_text(
        ["", "<i>Step 1</i> <b>New design</b>", "<i>Step 1</i> <b>New design</b>", "<i>Step 1</i> <b>New design</b>"],
        font_size="18",
        text_align="center",
    )

    selectbox_input(
        parameter_name="q1",
        parmater_description="Use",
        options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
        result=input_paramters,
    )

    number_input(
        parameter_name="l1",
        parmater_description="Floor span [m]",
        min_value=2.0,
        max_value=8.0,
        default_value=6.0,
        step=0.5,
        result=input_paramters,
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
        result=input_paramters,
    )

    selectbox_input(
        parameter_name="year",
        parmater_description="Construction period (design steel yield strength)",
        options=("1956-1967 (300 N/mm²)", "1968-1988 (390 N/mm²)", "1988-2023 (435 N/mm²)"),
        index=1,
        result=input_paramters,
    )

    number_input(
        parameter_name="l0",
        parmater_description="Slab span [m]",
        min_value=2.0,
        max_value=8.0,
        default_value=3.0,
        step=0.1,
        result=input_paramters,
    )

    number_input(
        parameter_name="hsreuse",
        parmater_description="Slab thickness [cm]",
        min_value=0.14,
        max_value=0.30,
        default_value=0.14,
        step=0.02,
        result=input_paramters,
    )

    number_input(
        parameter_name="tpdist_beton_reuse",
        parmater_description="Transportation distance the new design [km]",
        min_value=0,
        max_value=1000,
        default_value=20,
        step=5,
        result=input_paramters,
    )

    html_text(
        [
            "",
            "<i>Step 3</i> <b>Steel profiles</b>",
            "<i>Step 3</i> <b>Steel profiles</b>",
            "<i>Step 3</i> <b>Steel profiles</b>",
        ],
        font_size="18",
        text_align="center",
    )

    def with_steel_profil_distance():
        pass
        # print(result[0])

    selectbox_input(
        parameter_name="steelprofile_type",
        parmater_description="Type of steel profiles",
        options=("Reused steel profiles", "New steel profile"),
        index=1,
        result=input_paramters,
        on_change=with_steel_profil_distance(),
    )

    tpdist_metal_reuse_disabled = [
        True if input_paramters[i].get("steelprofile_type") == 1 else False for i in range(0, 3)
    ]

    number_input(
        parameter_name="tpdist_metal_reuse",
        parmater_description="Steel profiles [km]",
        min_value=0,
        max_value=1000,
        default_value=80,
        step=1,
        result=input_paramters,
        disabled=tpdist_metal_reuse_disabled,
    )

    st.markdown("#")

    with st.container():
        button_pressed = st.button("Run Simulations", use_container_width=True)
        st.markdown("#")

    if button_pressed:
        input_paramters = run_simulation(input_parameters=input_paramters)
        display_results(simulation_result=input_paramters)


def header():
    """
    This function creates the header of the app.
    """
    st.write(css,unsafe_allow_html=True)
    
    col0, col1, col2 = st.columns([10, 1, 1])
    with col0:
        col0.markdown("#")

        html_text(text="<b>Flo:RE Calculator <b>", color="#010302", font_size="30", text_align="Left", column=False)
        html_text(
            text=(
                "Flo:RE Calculator is an  Automated Pre-design and Embodied-carbon Tool for Floors made of REused cut"
                " concrete pieces"
            ),
            color=PAGE_THEME_COLOR,
            font_size="22",
            text_align="Left",
            column=False,
        )

    with col1:
        col1.markdown("#")
        html_text(
            text="""
                <img decoding="async"  height="100"
                src="https://www.epfl.ch/about/overview/wp-content/uploads/2020/07/logo-epfl-1024x576.png"
                class="attachment-full size-full" alt="EPFL" loading="lazy" data-recalc-dims="1">
                """,
            color=PAGE_THEME_COLOR,
            font_size="22",
            text_align="Left",
            column=False,
        )

    with col2:
        col2.markdown("#")
        html_text(
            text="""
                <a href="https://github.com/EPFL-ENAC/sxl-recrete-prognosis">
                <img decoding="async" width="100" height="100"
                src="https://github.blog/wp-content/uploads/2008/12/forkme_right_red_aa0000.png?resize=149%2C149"
                class="attachment-full size-full" alt="Fork me on GitHub" loading="lazy" data-recalc-dims="1"></a>
                """,
            color=PAGE_THEME_COLOR,
            font_size="22",
            text_align="Left",
            column=False,
        )


def footer():
    """
    This function creates the footer of the app.
    """
    st.markdown("---")
    html_text(
        text=(
            "©EPFL, 2023 // Küpfer, C., Bertola, N., Fivet, C., [under review]. [insert final paper title]. [insert"
            " link to article]"
        ),
        font_size="18",
        text_align="Left",
        column=False,
    )


def page():
    """
    This function is the main function of the app. It calls all the other functions to create the app.
    """
    header()

    tab1, tab2, tab3, tab4 = st.tabs(["Simulations", "About Flo\\:RE", "Journal paper", "Contact"])
    with tab1:
        main_part()
    with tab2:
        about_section()

    with tab3:
        paper_section()

    with tab4:
        contact_section()

    footer()
    

if __name__ == "__main__":
    page()
