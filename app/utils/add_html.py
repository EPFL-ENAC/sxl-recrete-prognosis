import streamlit as st


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
