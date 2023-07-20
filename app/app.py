import plotly.express as px
import streamlit as st
from alias import alias
from drawing import plot_drawing
from process import processing

# Define page layout
st.set_page_config(layout="wide")
st.title("Reused as-cut cast-in-place concrete slab pieces")


def add_selectbox(parameter_name: str, parmater_description: str, options: tuple, result: list):
    """ "Create a row of select boxes for the simulation and save the chosen parameter under the result list.

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
                )
                result[i - 1][parameter_name] = alias.get(parameter_name).get(res)


def add_number_input(
    parameter_name: str,
    parmater_description: str,
    min_value: float,
    max_value: float,
    default_value: float,
    step: float,
    result: list,
):
    """Create a row of input numbers for the simulation and save the chosen parameter under the result list.

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
                )
                result[i - 1][parameter_name] = res


def run_simulation(result: list, description: list):
    """This function takes the input parameters, run the simulation and display the results.

    Parameters
    ----------
    result : list
        List of the input parameters.
    description : list
        List containing the description of the results per line.
    """
    simulation_result = []
    for simulation_id, simulation_params in enumerate(result):
        simulation_result.append(processing(**simulation_params))

    for line, description_text in enumerate(description):
        st.markdown("---")
        col0, col1, col2, col3 = st.columns(4)
        col0.write(description_text)

        if line == 0:
            for simulation_id, column in enumerate([col1, col2, col3]):
                column.write(f"The selected system is : {simulation_result[simulation_id][0]}")

        if line == 1:
            for simulation_id, column in enumerate([col1, col2, col3]):
                fig = px.bar(
                    simulation_result[simulation_id][1],
                    y="values",
                    labels={"values": "Co2 emissions"},
                    color_discrete_sequence=["grey"],
                    text="values",
                )
                fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                fig.update_layout(xaxis_title="")
                column.plotly_chart(fig, use_container_width=True)

        if line == 2:
            for simulation_id, column in enumerate([col1, col2, col3]):
                fig = px.pie(
                    simulation_result[simulation_id][2],
                    values="values",
                    names=simulation_result[simulation_id][2].index,
                )
                column.plotly_chart(fig, use_container_width=True)

        if line == 3:
            for simulation_id, column in enumerate([col1, col2, col3]):
                fig = px.pie(
                    simulation_result[simulation_id][3],
                    values="values",
                    names=simulation_result[simulation_id][3].index,
                )
                column.plotly_chart(fig, use_container_width=True)

        if line == 4:
            for simulation_id, column in enumerate([col1, col2, col3]):
                drawing = simulation_result[simulation_id][4]
                fig2 = plot_drawing(l1=drawing.get("l1"), h=drawing.get("h"), number_part=drawing.get("number_part"))
                column.plotly_chart(fig2, use_container_width=True)


col0, col1, col2, col3 = st.columns(4)
col0.write(" ")
col1.write("Simulation no 1")
col2.write("Simulation no 2")
col3.write("Simulation no 3")


result = [{} for i in range(3)]


add_selectbox(
    parameter_name="q0",
    parmater_description="Donor-structure design use",
    options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
    result=result,
)
add_selectbox(
    parameter_name="year",
    parmater_description="Donor-structure construction period (design steel yield strength)",
    options=("1956-1967 (300 N/mm²)", "1968-1988 (390 N/mm²)", "1988-2023 (435 N/mm²)"),
    result=result,
)
add_number_input(
    parameter_name="l0",
    parmater_description="Donor-structure slab span [m]",
    min_value=2.0,
    max_value=8.0,
    default_value=3.0,
    step=0.5,
    result=result,
)

add_number_input(
    parameter_name="hsreuse",
    parmater_description="Donor-hsreuse",
    min_value=0.14,
    max_value=0.22,
    default_value=0.14,
    step=0.02,
    result=result,
)

add_selectbox(
    parameter_name="q1",
    parmater_description="New-design use",
    options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
    result=result,
)

add_number_input(
    parameter_name="l1",
    parmater_description="New-design floor span [m]",
    min_value=2.0,
    max_value=8.0,
    default_value=6.0,
    step=0.5,
    result=result,
)

add_number_input(
    parameter_name="tpdist_beton_reuse",
    parmater_description="Cut reinforced-concrete pieces [km]",
    min_value=0,
    max_value=1000,
    default_value=20,
    step=1,
    result=result,
)

add_number_input(
    parameter_name="tpdist_metal_reuse",
    parmater_description="Steel profiles [km]",
    min_value=0,
    max_value=1000,
    default_value=80,
    step=1,
    result=result,
)


with st.container():
    button_pressed = st.button("Run Simulations", use_container_width=True)


if button_pressed:
    description = [
        "Selected system",
        "Comparaison of the impact",
        "Comparaison of the impact for reused elements",
        "Comparaison of the impact for new elements",
        "Drawing",
    ]

    run_simulation(result=result, description=description)
