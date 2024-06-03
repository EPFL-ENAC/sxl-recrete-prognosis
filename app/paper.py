import os

import streamlit as st
import yaml
from utils.add_html import html_text

LOCAL_FOLDER_PATH = os.path.dirname(__file__)
with open(os.path.join(LOCAL_FOLDER_PATH, "app_layout_config.yml")) as f:
    config = yaml.safe_load(f)

PAGE_THEME_COLOR = f"#{config.get('page_color')}"


def paper_section():
    with st.container():
        html_text(
            text="""
                <br> <b>Journal paper</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
                More details on the floor systems and the design procedure are available in our Journal Paper published in the Journal of Cleaner Production:
<br>
Küpfer, Bertola & Fivet  (2024). Reuse of cut concrete slabs in new buildings for circular ultra-low-carbon floor designs. Journal of Cleaner Production, 448, 141566. Doi: 10.1016/j.jclepro.2024.141566
<br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        html_text(
            text="""
                <br> <b>Paper highlights</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
        <ul>
            <li>Reusing concrete pieces is an untapped circular resource-management strategy</li>
            <li>New load-bearing floor systems made of reused as-cut concrete pieces are introduced</li>
            <li>A procedure determines the allowable span for concrete pieces reused in bending</li>
            <li>A parametric study shows upfront greenhouse gas emissions as low as 5 kgCO2e/m2</li>
            <li>On average, embodied carbon is reduced by 80 % compared to a traditional concrete slab”</li>
        </ul>
                """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
                <br> <b>Funding</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
                This research was supported by the Swiss National Science Foundation (SNSF) through the doc.CH program (grant number P0ELP1_192059) and by the EPFL through the ENAC Interdisciplinary Cluster Grant program (grant name RE:CRETE Prognosis).
                """,
            font_size="18",
            text_align="Left",
            column=False,
        )

