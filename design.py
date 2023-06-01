import streamlit as st

from text_sections import (
    design_text,
)

# arrow_size = 0.048,
# arrow_nudge_from_text = 0.065,
# sums_settings = sum_tile_settings(),
# intensity_by

# darkness = 0.8


def design_section(
    num_classes,
    predictions_are_probabilities,
):
    output = {}

    with st.form(key="settings_form"):
        design_text()
        col1, col2 = st.columns(2)
        with col1:
            output["selected_classes"] = st.multiselect(
                "Select classes (min=2, order is respected)",
                options=st.session_state["classes"],
                default=st.session_state["classes"],
                help="Select the classes to create the confusion matrix for. "
                "Any observation with either a target or prediction "
                "of another class is excluded.",
            )
        with col2:
            if (
                st.session_state["input_type"] == "data"
                and predictions_are_probabilities
            ):
                output["prob_of_class"] = st.selectbox(
                    "Probabilities are of (not working)",
                    options=st.session_state["classes"],
                    index=1,
                )
            else:
                output["prob_of_class"] = None

        with st.expander("Elements"):
            default_elements = [
                "Counts",
                "Normalized Counts (%)",
                "Zero Shading",
                "Arrows",
            ]
            if num_classes < 6:
                # Percentages clutter too much with many classes
                default_elements += [
                    "Row Percentages",
                    "Column Percentages",
                ]
            elements_to_add = st.multiselect(
                "Add the following elements",
                options=[
                    "Sum Tiles",
                    "Counts",
                    "Normalized Counts (%)",
                    "Row Percentages",
                    "Column Percentages",
                    "Zero Shading",
                    "Zero Percentages",
                    "Zero Text",
                    "Arrows",
                ],
                default=default_elements,
            )

            st.markdown("""---""")

            col1, col2, col3 = st.columns(3)
            with col1:
                counts_on_top = st.checkbox(
                    "Counts on top (not working)",
                    help="Whether to switch the positions of the counts and normalized counts (%). "
                    "That is, the counts become the big centralized numbers and the "
                    "normalized counts go below with a smaller font size.",
                )
            with col2:
                diag_percentages_only = st.checkbox(
                    "Diagonal row/column percentages only"
                )

        with st.expander("Text"):
            col1, col2, col3 = st.columns(3)
            with col1:
                output["num_digits"] = st.number_input(
                    "Digits", value=2, help="Number of digits to round percentages to."
                )
            with col2:
                rotate_y_text = st.checkbox("Rotate y text", value=True)
            with col3:
                place_x_axis_above = st.checkbox("Place X axis on top", value=True)

        with st.expander("Fonts"):
            font_dicts = {}
            for font_type in ["Counts", "Normalized (%)", "Row Percentage", "Column Percentage"]:
                st.subheader(font_type)
                num_cols = 3
                font_dicts[font_type] = font_inputs(key_prefix=font_type)
                for i, (setting_name, setting_widget) in enumerate(
                    font_dicts[font_type].items()
                ):
                    if i % num_cols == 0:
                        cols = st.columns(num_cols)
                    with cols[i % num_cols]:
                        setting_widget()

                st.markdown("""---""")

        with st.expander("Tiles"):
            col1, col2, col3 = st.columns(3)
            with col1:
                pass
            with col2:
                output["intensity_by"] = st.selectbox("Intensity based on", options=["Counts", "Normalized (%)"])
            with col3:
                output["darkness"] = st.slider(
                    "Darkness",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.8,
                    step=0.01,
                    help="How dark the darkest colors should be, between 0 and 1, where 1 is darkest.",
                )

            st.markdown("""---""")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                output["tile_border_add"] = st.checkbox("Add tile borders", value=False)
            with col2:
                output["tile_border_color"] = st.color_picker(
                    "Border color", value="#000000"
                )
            with col3:
                output["tile_border_size"] = st.slider(
                    "Border size",
                    min_value=0.0,
                    max_value=3.0,
                    value=0.1,
                    step=0.01,
                )
            with col4:
                output["tile_border_linetype"] = st.selectbox(
                    "Border linetype",
                    options=[
                        "solid",
                        "dashed",
                        "dotted",
                        "dotdash",
                        "longdash",
                        "twodash",
                    ],
                )

        output["element_flags"] = [
            key
            for key, val in {
                "--add_sums": "Sum Tiles" in elements_to_add,
                "--add_counts": "Counts" in elements_to_add,
                "--add_normalized": "Normalized Counts (%)" in elements_to_add,
                "--add_row_percentages": "Row Percentages" in elements_to_add,
                "--add_col_percentages": "Column Percentages" in elements_to_add,
                "--add_zero_percentages": "Zero Percentages" in elements_to_add,
                "--add_zero_text": "Zero Text" in elements_to_add,
                "--add_zero_shading": "Zero Shading" in elements_to_add,
                "--add_arrows": "Arrows" in elements_to_add,
                "--counts_on_top": counts_on_top,
                "--diag_percentages_only": diag_percentages_only,
            }.items()
            if val
        ]

        output["palette"] = st.selectbox(
            "Color Palette",
            options=["Blues", "Greens", "Oranges", "Greys", "Purples", "Reds"],
        )

        # Ask for output parameters
        # TODO: Set default based on number of classes and sum tiles
        col1, col2, col3 = st.columns(3)
        with col1:
            output["width"] = st.number_input(
                "Width (px)", value=1200 + 100 * (num_classes - 2)
            )
        with col2:
            output["height"] = st.number_input(
                "Height (px)", value=1200 + 100 * (num_classes - 2)
            )
        with col3:
            output["dpi"] = st.number_input("DPI (not working)", value=320)

        if st.form_submit_button(label="Generate plot"):
            st.session_state["step"] = 3

        return output


def font_inputs(key_prefix: str):
    return {
        "color": lambda: st.color_picker("Color", key=f"{key_prefix}_color"),
        "bold": lambda: st.checkbox("Bold", key=f"{key_prefix}_bold"),
        "cursive": lambda: st.checkbox("Italics", key=f"{key_prefix}_italics"),
        "size": lambda: st.number_input("Size", key=f"{key_prefix}_size"),
        "nudge_x": lambda: st.number_input(
            "Nudge on x-axis", key=f"{key_prefix}_nudge_x"
        ),
        "nudge_y": lambda: st.number_input(
            "Nudge on y-axis", key=f"{key_prefix}_nudge_y"
        ),
        "alpha": lambda: st.slider(
            "Transparency", min_value=0, max_value=1, value=1, key=f"{key_prefix}_alpha"
        ),
        "prefix": lambda: st.text_input("Prefix", key=f"{key_prefix}_prefix"),
        "suffix": lambda: st.text_input("Suffix", key=f"{key_prefix}_suffix"),
    }
