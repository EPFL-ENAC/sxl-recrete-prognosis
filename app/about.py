import os

import streamlit as st
import yaml
from PIL import Image
from utils.add_html import html_text

LOCAL_FOLDER_PATH = os.path.dirname(__file__)
with open(os.path.join(LOCAL_FOLDER_PATH, "app_layout_config.yml")) as f:
    config = yaml.safe_load(f)

PAGE_THEME_COLOR = f"#{config.get('page_color')}"


def about_section():
    # html_path = os.path.join(LOCAL_FOLDER_PATH, "static", "header.html")
    # with open(html_path, "r") as f:
    #     html_content = f.read()
    # st.components.v1.html(html_content, width=None, height=300, scrolling=False)

    # st.components.v1.iframe("static/header.html", height=200, scrolling=False)

    with st.container():
        html_text(
            text="""
            <br> <b>About the floor systems</b><br>
            """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        image_path = os.path.join(LOCAL_FOLDER_PATH, "static", "slab.png")

        if os.path.exists(image_path):
            st.image(Image.open(image_path))

        html_text(
            text="""At EPFL, we developed a new construction systems for floors made of reused cut
            concrete elements. Depending on the the design project,
            the floor systems only reuse concrete cut from existing slabs or combine it
            with either new or reused steel profiles.""",
            font_size="18",
            text_align="Left",
            column=False,
        )
        image_path = os.path.join(LOCAL_FOLDER_PATH, "static", "reused_steel_profile.png")

        if os.path.exists(image_path):
            st.image(Image.open(image_path))

        html_text(
            text="""
            The simulation calculator is an automated tool to pre-design floor systems that match the specificities of your new design and of your concrete or steel donor structure. Enter your design and donor-structure specificities and the calculator will suggest a floor system and estimate its embodied carbon.
More details on the in our peer-reviewed paper: Küpfer, Bertola & Fivet (2024). Reuse of cut concrete slabs in new buildings for circular ultra-low-carbon floor designs. Journal of Cleaner Production, 448, 141566. <a href="https://doi.org/10.1016/j.jclepro.2024.141566"> Doi : 10.1016/j.jclepro.2024.141566</a>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
            <br> <b>Ressource diagnostic of concrete structures</b><br>
            """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            At the Structural Xploration, we developped a protocol for the ressource diagnostic of concrete structures. Check our peer-reviewed journal paper for more details : Devènes, Bastien-Masse & Fivet (2024). Reusability assessment of reinforced concrete components prior to deconstruction from obsolete buildings. Journal of Building Engineering, 84, 108584.
            <a href="https://doi.org/10.1016/j.jobe.2024.108584"> Doi : 10.1016/j.jobe.2024.108584</a>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
            <br><b>Disclaimer</b><br>
            """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            The calculator never replaces the work of a civil engineer and is only conceived as an early pre-design stage supporting tool. <br>
            No composite action between concrete and steel is assumed. <br />
            Donor structures are assumed in good condition and designed based
            on Swiss standards at the time of constuction. <br />
            All material properties must be verified with appropriate testing methods. <br/>
            Concrete slabs are assumed to be flat, unprestressed,
            with unidirectional continuous reinforcement.
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
            <br> <b>Credits </b><br>
            """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            This web application is the result of dedicated effort and collaboration: <br>Code development:
            <li>Célia Küpfer (Structural Xploration Lab, EPFL)</li>
            <li>Numa Bertola (Structural Maintenance and Safety Laboratory, EPFL)</li>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            Academic supervision:
            <li>Corentin Fivet (Structural Xploration Lab, EPFL)</li>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            Software implementation:
            <li>Régis Longchamp (ENAC-IT4Research, EPFL)</li>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
            <br> <b>Source code </b><br>
            """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            You can also find the source code for this project on GitHub:
            <a href="https://github.com/EPFL-ENAC/sxl-recrete-prognosis">
            https://github.com/EPFL-ENAC/sxl-recrete-prognosis</a>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
