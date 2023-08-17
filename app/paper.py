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
                Coming soon<br>
                """,
            font_size="18",
            text_align="Left",
            column=False,
        )
