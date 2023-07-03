import plotly.express as px
import streamlit as st
from alias import alias
from CERES_casestudy import processing
from drawing import plot_drawing

# Define page layout
st.set_page_config(layout="wide")
st.title("Reused as-cut cast-in-place concrete slab pieces")
result = {}


def run_simulation(result: list, columns: list):
    for i in result:
        simulation_params = result[i]
        simulation_result = processing(**simulation_params)

        if simulation_result:
            column = columns[i]
            column.markdown("---")
            column.write(f"The selected system is : {simulation_result[0]}")

            fig = px.bar(
                simulation_result[1], y="values", title="Comparaison of the impact", labels={"values": "Co2 emissions"}
            )
            column.plotly_chart(fig, use_container_width=True)

            fig = px.pie(
                simulation_result[2],
                values="values",
                names=simulation_result[2].index,
                title="Comparaison of the impact for reused elements",
            )
            column.plotly_chart(fig, use_container_width=True)

            fig = px.pie(
                simulation_result[3],
                values="values",
                names=simulation_result[3].index,
                title="Comparaison of the impact for new elements",
            )
            column.plotly_chart(fig, use_container_width=True)

            drawing = simulation_result[4]
            fig2 = plot_drawing(l1=drawing.get("l1"), h=drawing.get("h"), number_part=drawing.get("number_part"))

            column.plotly_chart(fig2, use_container_width=True)


# Define the number of simulations
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        num_columns = st.number_input(
            " 1️⃣ Choose the number of simulations", min_value=1, max_value=5, value=1, step=1
        )
    with col2:
        st.write(" 2️⃣ Define the simulation parameters")
        st.write(" ↓ below ↓")
    with col3:
        st.write(" 3️⃣ Run the simulations")
        button_pressed = st.button("Run Simulations")

    st.markdown("---")

columns = st.columns(num_columns)

# Define the simulation parameters
for i, column in enumerate(columns):
    simulation_id = i + 1

    if simulation_id == 1:
        label_visibility = "visible"
        suffix = ""
    else:
        label_visibility = "hidden"
        suffix = f"{i}"

    column.write(f"Parameters for simulation no {simulation_id}")
    q0 = column.selectbox(
        label=f"Donor-structure design use{suffix}",
        options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
        label_visibility=label_visibility,
    )
    year = column.selectbox(
        label=f"Donor-structure construction period (design steel yield strength){suffix}",
        options=("1956-1967 (300 N/mm²)", "1968-1988 (390 N/mm²)", "1988-2023 (435 N/mm²)"),
        label_visibility=label_visibility,
    )
    l0 = column.number_input(
        label=f"Donor-structure slab span [m]{suffix}",
        min_value=2.0,
        max_value=8.0,
        value=3.0,
        step=0.5,
        label_visibility=label_visibility,
    )
    hsreuse = column.number_input(
        label=f"Donor-hsreuse{suffix}",
        min_value=0.0,
        max_value=1.0,
        value=0.15,
        step=0.01,
        label_visibility=label_visibility,
    )
    q1 = column.selectbox(
        label=f"New-design use{suffix}",
        options=("Housing (2 kN/m²)", "Office (3 kN/m²)"),
        label_visibility=label_visibility,
    )
    l1 = column.number_input(
        label=f"New-design floor span [m]{suffix}",
        min_value=2.0,
        max_value=8.0,
        value=6.0,
        step=0.5,
        label_visibility=label_visibility,
    )
    tpdist_beton_reuse = column.number_input(
        f"Cut reinforced-concrete pieces [km]{suffix}",
        value=20,
        min_value=0,
        max_value=1000,
        step=1,
        label_visibility=label_visibility,
    )
    tpdist_metal_reuse = column.number_input(
        f"Steel profiles [km]{suffix}", value=80, min_value=0, max_value=1000, step=1, label_visibility=label_visibility
    )

    result[i] = {
        "l0": l0,
        "l1": l1,
        "hsreuse": hsreuse,
        "year": alias.get("year").get(year),
        "q0": alias.get("q0").get(q0),
        "q1": alias.get("q1").get(q1),
        "tpdist_beton_reuse": tpdist_beton_reuse,
        "tpdist_metal_reuse": tpdist_metal_reuse,
    }


if button_pressed:
    run_simulation(result=result, columns=columns)
