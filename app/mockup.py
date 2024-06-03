import os

import streamlit as st
import yaml
from utils.add_html import html_text
from PIL import Image
from streamlit_carousel import carousel

LOCAL_FOLDER_PATH = os.path.dirname(__file__)
with open(os.path.join(LOCAL_FOLDER_PATH, "app_layout_config.yml")) as f:
    config = yaml.safe_load(f)

PAGE_THEME_COLOR = f"#{config.get('page_color')}"


def mockup_section():
    with st.container():
        html_text(
            text="""
                <br> <b>New FLO:RE mock-up: we built it!</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
                <br> <b>A 30-m2 mock-up of an office-building floor made of reused concrete and reused steel</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            To further develop and verify our theoretical work presented in our journal paper , we designed, built and tested a 30-m2 mock-up made of locally-salvaged reused reinforced concrete elements and reused steel profiles. The mock-up is designed as an office building floor. The reinforced concrete elements were saw-cut from the roof slab of a building about to be demolished, and the steel profiles were salvaged from an industrial hall undergoing deconstruction.
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        images = [
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/a_FLORE04.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/b_FLORE32.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/c_FLORE03.png.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/d_FLORE33.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/e_FLORE10.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/f_FLORE11.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/g_FLORE14.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/h_FLORE24.jpg.webp",
            "https://enacit4r-cdn.epfl.ch/sxl-recrete-prognosis/2024-04-23/i_FLORE26.jpg.webp"
        ]
        
        test_items = [
            dict(title="", text="© EPFL", img=image,
                 interval=None)
            for image in images
                     ]

        carousel(items=test_items, width=1)

        html_text(
            text="""
    Altogether, the mock-up's construction demonstrates the system's technical feasibility. The mock-up's structural performance was verified through material testing and load tests. A detailed Life-Cycle Assessment confirmed the previously simulated gains: with a transportation distance of 100 km for the reused elements, the mock-up's upfront embodied carbon is 12 kgCO2e/m2, 84 % lower than that of a conventional new RC flat slab.
Thanks to dry connections, the system is not only made with 99 % (in terms of weight) of reused materials, but it is also entirely dismantlable and reusable, thus fully circular.

More details and journal paper coming soon!
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )

        image_path = os.path.join(LOCAL_FOLDER_PATH, "static", "d_FLORE33.jpg.webp")

        if os.path.exists(image_path):
            st.image(Image.open(image_path), caption="the video is not ready yet.. we will send you a link when ready: © EPFL", use_column_width=True)


        html_text(
            text="""
                <br> <b>Team and partners</b><br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
            color=PAGE_THEME_COLOR,
        )

        html_text(
            text="""
            <i>FLO:RE Mock-up team</i>:<br/>
Célia Küpfer (SXL, EPFL), Dr. Malena Bastien-Masse (SXL, EPFL), Prof. Numa Bertola (MCS, EPFL + Uni. Luxembourg), Prof. Corentin Fivet (SXL, EPFL)            
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            <i>Partners</i>:<br/>
            The sourcing of the reused components was made possible thanks to our industrial partners: Diamcoupe SA, La Ressourcerie, the Lyon 106-108 Consortium (aeby+mouthon architectes , SOTRAG SA, Perret SA, Thomas Jundt ingénieurs civils SA, Favre+Guth architecture SA), Küpfer Géomètres SA, and atba architecture + énergie.
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            <i>The FLO:RE Mock-up team also thanks</i>:<br/>
            <ul>
            <li>Claude-Alain Jacot and Stéphane Pilloud, technicians at the Atelier Popup of the Smart Living Lab, Fribourg (Switzerland), for the mock-up construction</li>
            <li>Frédérique Dubugnon and Gilles Guignet, technicians at the Structural Engineering Platform (GIS) at EPFL for the assistance during the material and mock-up testing
</li>
            <li>Selimcan Ozden and Dr. Nenad Bijelic, researchers at RessLab (EFPL), and Prof. Dimitrios Lignos, director of the RessLab, for the steel profile testing.</li>
            </ul>
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )
        html_text(
            text="""
            <i>Funding</i>:<br/>
            This research was supported by the Swiss National Science Foundation (SNSF) through the doc.CH program (grant number P0ELP1_192059) and by the EPFL through the ENAC Interdisciplinary Cluster Grant program (grant name RE:CRETE Prognosis).”
            """,
            font_size="18",
            text_align="Left",
            column=False,
        )