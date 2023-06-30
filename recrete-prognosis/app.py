import streamlit as st
import json
import time
from CERES_casestudy import processing
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from drawing import plot_drawing


st.set_page_config(layout="wide")


st.title("Simulation App")


num_columns = st.number_input("Number of simulations", min_value=1, max_value=5, value=1, step=1)
columns = st.columns(num_columns)

result = {}


first_column = columns[0]


# alias = json.load(open("alias.json", "r"))
# print(alias)
alias = {
    "q0": {"Housing (2 kN/m²)": 2, "Office (3 kN/m²)": 3},
    "year": {"1956-1967 (300 N/mm²)": 1, "1968-1988 (390 N/mm²)": 2, "1988-2023 (435 N/mm²)": 3},
    "q1": {"Housing (2 kN/m²)": 2, "Office (3 kN/m²)": 3},
}


for i, column in enumerate(columns):
    simulation_id = i + 1

    if simulation_id == 1:
        label_visibility = "visible"
        suffix = ""
    else:
        label_visibility = "hidden"
        suffix = f"{i}"

    column.write(f"Simulation {simulation_id}")
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

if st.button("Run Simulations"):
    for i in result:
        simulation_params = result[i]
        simulation_result = processing(**simulation_params)

        if simulation_result:
            column = columns[i]

            fig = px.bar(simulation_result[0], y="val",title="Comparaison of the impact",labels={'val':'Co2 emissions'})
            column.plotly_chart(fig, use_container_width=True)

            fig = px.pie(simulation_result[1], values="val", names="lab")
            column.plotly_chart(fig, use_container_width=True)


            drawing = simulation_result[2]
            fig2  = plot_drawing(l1 = drawing.get("l1"),
                               h = drawing.get("h"),
                               number_part=drawing.get("number_part"))
      
            

      
            
            column.plotly_chart(fig2, use_container_width=True)



