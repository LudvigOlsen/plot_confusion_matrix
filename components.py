import streamlit as st
from streamlit_toggle import st_toggle_switch


def add_toggle_vertical(label, key, default, cols=[2, 5]):
    st.markdown(f"<p style='font-size:0.85em;'>{label}</p>", unsafe_allow_html=True)
    col1, _ = st.columns(cols)
    with col1:
        return st_toggle_switch(
            " ",
            default_value=default,
            key=key,
            label_after=True,
            inactive_color="#eb5a53",
        )


def add_toggle_horizontal(label, key, default):
    return st_toggle_switch(
        label=label,
        default_value=default,
        key=key,
        label_after=True,
        inactive_color="#eb5a53",
    )
