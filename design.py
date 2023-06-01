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

        output["palette"] = st.selectbox(
            "Color Palette",
            options=["Blues", "Greens", "Oranges", "Greys", "Purples", "Reds"],
        )

        # Ask for output parameters
        # TODO: Set default based on number of classes and sum tiles
        col1, col2, col3 = st.columns(3)
        with col1:
            output["width"] = st.number_input(
                "Width (px)", value=1200 + 100 * (num_classes - 2), step=50
            )
        with col2:
            output["height"] = st.number_input(
                "Height (px)", value=1200 + 100 * (num_classes - 2), step=50
            )
        with col3:
            output["dpi"] = st.number_input("DPI (not working)", value=320, step=10)

        st.write(" ")  # Slightly bigger gap between the two sections
        col1, col2, col3 = st.columns(3)
        with col1:
            output["show_counts"] = st.checkbox("Show Counts", value=True)
        with col2:
            output["show_normalized"] = st.checkbox("Show Normalized (%)", value=True)
        with col3:
            output["show_sums"] = st.checkbox(
                "Show Sum Tiles",
                value=False,
                help="Show extra row and column with the "
                "totals for that row/column.",
            )

        st.markdown("""---""")
        st.markdown("**Advanced**:")

        with st.expander("Elements"):
            col1, col2 = st.columns(2)
            with col1:
                output["rotate_y_text"] = st.checkbox("Rotate y-axis text", value=True)
                output["place_x_axis_above"] = st.checkbox(
                    "Place x-axis on top", value=True
                )
                output["counts_on_top"] = st.checkbox(
                    "Counts on top (not working)",
                    help="Whether to switch the positions of the counts and normalized counts (%). "
                    "The counts become the big centralized numbers and the "
                    "normalized counts go below with a smaller font size.",
                )
            with col2:
                output["num_digits"] = st.number_input(
                    "Digits", value=2, help="Number of digits to round percentages to."
                )

            st.markdown("""---""")

            col1, col2 = st.columns(2)
            with col1:
                st.write("Row and column percentages:")
                output["show_row_percentages"] = st.checkbox(
                    "Show row percentages", value=num_classes < 6
                )
                output["show_col_percentages"] = st.checkbox(
                    "Show column percentages", value=num_classes < 6
                )
                output["show_arrows"] = st.checkbox("Show arrows", value=True)
                output["diag_percentages_only"] = st.checkbox(
                    "Diagonal row/column percentages only"
                )
            with col2:
                output["arrow_size"] = (
                    st.slider(
                        "Arrow size",
                        value=0.048 * 10,
                        min_value=0.03 * 10,
                        max_value=0.06 * 10,
                        step=0.001 * 10,
                    )
                    / 10
                )
                output["arrow_nudge_from_text"] = (
                    st.slider(
                        "Arrow nudge from text",
                        value=0.065 * 10,
                        min_value=0.00,
                        max_value=0.1 * 10,
                        step=0.001 * 10,
                    )
                    / 10
                )

        with st.expander("Tiles"):
            col1, col2, col3 = st.columns(3)
            with col1:
                pass
            with col2:
                output["intensity_by"] = st.selectbox(
                    "Intensity based on", options=["Counts", "Normalized (%)"]
                )
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
                output["show_tile_border"] = st.checkbox(
                    "Add tile borders", value=False
                )
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

            st.markdown("""---""")

            st.write("Sum tile settings:")

            col1, col2 = st.columns(2)
            with col1:
                output["sum_tile_palette"] = st.selectbox(
                    "Color Palette",
                    key="sum_tiles_color_palette",
                    options=["Greens", "Oranges", "Greys", "Purples", "Reds", "Blues"],
                )
            with col2:
                output["sum_tile_label"] = st.text_input(
                    "Label",
                    value="Σ",
                    key="sum_tiles_label",
                )

            #   label = NULL,
            #   tile_fill = NULL,
            #   font_color = NULL,
            #   tile_border_color = NULL,
            #   tile_border_size = NULL,
            #   tile_border_linetype = NULL,
            #   tc_tile_fill = NULL,
            #   tc_font_color = NULL,
            #   tc_tile_border_color = NULL,
            #   tc_tile_border_size = NULL,
            #   tc_tile_border_linetype = NULL

        with st.expander("Zero Counts"):
            st.write("Special settings for tiles where the count is 0:")
            col1, col2, col3 = st.columns(3)
            with col1:
                output["show_zero_shading"] = st.checkbox("Add shading", value=True)
            with col2:
                output["show_zero_text"] = st.checkbox(
                    "Show text",
                    value=False,
                    help="Whether to show counts, normalized (%), etc.",
                )
            with col3:
                output["show_zero_percentages"] = st.checkbox(
                    "Show row/column percentages",
                    value=False,
                    help="Only relevant when row/column percentages are enabled.",
                )

        with st.expander("Fonts"):
            font_dicts = {}
            font_types = [
                "Counts",
                "Normalized (%)",
                "Row Percentage",
                "Column Percentage",
            ]
            for font_type in font_types:
                st.subheader(font_type)
                num_cols = 3
                font_dicts[font_type] = font_inputs(key_prefix=font_type)
                for i, (_, setting_widget) in enumerate(font_dicts[font_type].items()):
                    if i % num_cols == 0:
                        cols = st.columns(num_cols)
                    with cols[i % num_cols]:
                        setting_widget()

                if font_type != font_types[-1]:
                    st.markdown("""---""")

        st.markdown("""---""")

        if st.form_submit_button(label="Generate plot"):
            st.session_state["step"] = 3

        if st.session_state["step"] >= 3:
            output["design_ready"] = True
            if output["show_sums"] and output["sum_tile_palette"] == output["palette"]:
                st.error(
                    "The color palettes (background colors) "
                    "for the tiles and sum tiles are identical. "
                    "Please select a different color palette for "
                    "the sum tiles under **Tiles** >> *Sum tile settings*."
                )
                output["design_ready"] = False

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
