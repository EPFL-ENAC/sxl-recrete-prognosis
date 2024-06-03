import os

import streamlit as st
import yaml
from utils.add_html import html_text

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
                A 30-m2 mock-up of an office-building floor made of reused concrete and reused steel<br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
        )
