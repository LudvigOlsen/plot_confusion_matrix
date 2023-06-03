from typing import List, Callable, Any, Tuple
import json
import streamlit as st

from text_sections import (
    design_text,
)


def _add_select_box(
    key: str,
    label: str,
    default: Any,
    options: List[Any],
    get_setting_fn: Callable,
    type_=str,
):
    """
    Add selectbox with selection of default value from setting function.
    """
    chosen_default = get_setting_fn(
        key=key,
        default=default,
        type_=type_,
        options=options,
    )
    return st.selectbox(
        label, options=options, index=options.index(chosen_default), key=key
    )


def design_section(
    num_classes,
    predictions_are_probabilities,
    design_settings_store_path,
):
    output = {}

    with st.form(key="settings_upload_form"):
        design_text()
        uploaded_settings_path = st.file_uploader(
            "Upload design settings", type=["json"]
        )
        # TODO: Allow resetting settings!
        if st.form_submit_button(label="Apply settings"):
            if uploaded_settings_path is not None:
                uploaded_design_settings = json.load(uploaded_settings_path)
            else:
                st.warning("No settings were uploaded. Uploading settings is optional.")

    def get_uploaded_setting(key, default, type_=None, options=None):
        # NOTE: Must be placed here, to have `uploaded_design_settings` in locals

        if "uploaded_design_settings" in locals() and key in uploaded_design_settings:
            out = uploaded_design_settings[key]
            if type_ is not None:
                if not isinstance(out, type_):
                    st.warning(
                        f"An uploaded setting ({key}) had the wrong type. Using default value."
                    )
                    return default
            if options is not None:
                if out not in options:
                    st.warning(
                        f"An uploaded setting ({key}) was not a valid choice. Using default value."
                    )
                    return default
            return out
        return default

    with st.form(key="settings_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_classes = st.multiselect(
                "Select classes (min=2, order is respected)",
                options=st.session_state["classes"],
                default=st.session_state["classes"],
                help="Select the classes to create the confusion matrix for. "
                "Any observation with either a target or prediction "
                "of another class is excluded.",
            )
        with col2:
            prob_of_class = None
            # Not respected, so disabled for now
            # if (
            #     st.session_state["input_type"] == "data"
            #     and predictions_are_probabilities
            # ):
            #     prob_of_class = st.selectbox(
            #         "Probabilities are of (not working)",
            #         options=st.session_state["classes"],
            #         index=1,
            #     )
            # else:
            #     prob_of_class = None

        # Color palette
        output["palette"] = _add_select_box(
            key="palette",
            label="Color Palette",
            default="Blues",
            options=["Blues", "Greens", "Oranges", "Greys", "Purples", "Reds"],
            get_setting_fn=get_uploaded_setting,
            type_=str,
        )

        # Ask for output parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            output["width"] = st.number_input(
                "Width (px)",
                value=get_uploaded_setting(
                    key="width", default=1200 + 100 * (num_classes - 2), type_=int
                ),
                step=50,
            )
        with col2:
            output["height"] = st.number_input(
                "Height (px)",
                value=get_uploaded_setting(
                    key="width", default=1200 + 100 * (num_classes - 2), type_=int
                ),
                step=50,
            )
        with col3:
            output["dpi"] = st.number_input(
                "DPI (not working)",
                value=get_uploaded_setting(key="dpi", default=320, type_=int),
                step=10,
            )

        st.write(" ")  # Slightly bigger gap between the two sections
        col1, col2, col3 = st.columns(3)
        with col1:
            output["show_counts"] = st.checkbox(
                "Show Counts",
                value=get_uploaded_setting(key="show_counts", default=True, type_=bool),
            )
        with col2:
            output["show_normalized"] = st.checkbox(
                "Show Normalized (%)",
                value=get_uploaded_setting(
                    key="show_normalized", default=True, type_=bool
                ),
            )
        with col3:
            output["show_sums"] = st.checkbox(
                "Show Sum Tiles",
                value=get_uploaded_setting(key="show_sums", default=False, type_=bool),
                help="Show extra row and column with the "
                "totals for that row/column.",
            )

        st.markdown("""---""")
        st.markdown("**Advanced**:")

        with st.expander("Elements"):
            col1, col2 = st.columns(2)
            with col1:
                output["rotate_y_text"] = st.checkbox(
                    "Rotate y-axis text",
                    value=get_uploaded_setting(
                        key="rotate_y_text", default=True, type_=bool
                    ),
                )
                output["place_x_axis_above"] = st.checkbox(
                    "Place x-axis on top",
                    value=get_uploaded_setting(
                        key="place_x_axis_above", default=True, type_=bool
                    ),
                )
                output["counts_on_top"] = st.checkbox(
                    "Counts on top (not working)",
                    value=get_uploaded_setting(
                        key="counts_on_top", default=False, type_=bool
                    ),
                    help="Whether to switch the positions of the counts and normalized counts (%). "
                    "The counts become the big centralized numbers and the "
                    "normalized counts go below with a smaller font size.",
                )
            with col2:
                output["num_digits"] = st.number_input(
                    "Digits",
                    value=get_uploaded_setting(key="num_digits", default=2, type_=int),
                    help="Number of digits to round percentages to.",
                )

            st.markdown("""---""")

            col1, col2 = st.columns(2)
            with col1:
                st.write("Row and column percentages:")
                output["show_row_percentages"] = st.checkbox(
                    "Show row percentages",
                    value=get_uploaded_setting(
                        key="show_row_percentages", default=num_classes < 6, type_=bool
                    ),
                )
                output["show_col_percentages"] = st.checkbox(
                    "Show column percentages",
                    value=get_uploaded_setting(
                        key="show_col_percentages", default=num_classes < 6, type_=bool
                    ),
                )
                output["show_arrows"] = st.checkbox(
                    "Show arrows",
                    value=get_uploaded_setting(
                        key="show_arrows", default=True, type_=bool
                    ),
                )
                output["diag_percentages_only"] = st.checkbox(
                    "Diagonal row/column percentages only",
                    value=get_uploaded_setting(
                        key="diag_percentages_only", default=False, type_=bool
                    ),
                )
            with col2:
                output["arrow_size"] = (
                    st.slider(
                        "Arrow size",
                        value=get_uploaded_setting(
                            key="arrow_size", default=0.048 * 10, type_=float
                        ),
                        min_value=0.03 * 10,
                        max_value=0.06 * 10,
                        step=0.001 * 10,
                    )
                    / 10
                )
                output["arrow_nudge_from_text"] = (
                    st.slider(
                        "Arrow nudge from text",
                        value=get_uploaded_setting(
                            key="arrow_nudge_from_text", default=0.065 * 10, type_=float
                        ),
                        min_value=0.00,
                        max_value=0.1 * 10,
                        step=0.001 * 10,
                    )
                    / 10
                )

        with st.expander("Tiles"):
            col1, col2 = st.columns(2)
            with col1:
                output["intensity_by"] = _add_select_box(
                    key="intensity_by",
                    label="Intensity based on",
                    default="Counts",
                    options=["Counts", "Normalized (%)"],
                    get_setting_fn=get_uploaded_setting,
                    type_=str,
                )
            with col2:
                output["darkness"] = st.slider(
                    "Darkness",
                    min_value=0.0,
                    max_value=1.0,
                    value=get_uploaded_setting(
                        key="darkness", default=0.8, type_=float
                    ),
                    step=0.01,
                    help="How dark the darkest colors should be, between 0 and 1, where 1 is darkest.",
                )

            st.markdown("""---""")

            output["show_tile_border"] = st.checkbox(
                "Add tile borders",
                value=get_uploaded_setting(
                    key="show_tile_border", default=False, type_=bool
                ),
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                output["tile_border_color"] = st.color_picker(
                    "Border color",
                    value=get_uploaded_setting(
                        key="tile_border_color", default="#000000", type_=str
                    ),
                )
            with col2:
                output["tile_border_size"] = st.slider(
                    "Border size",
                    min_value=0.0,
                    max_value=3.0,
                    value=get_uploaded_setting(
                        key="tile_border_size", default=0.1, type_=float
                    ),
                    step=0.01,
                )
            with col3:
                output["tile_border_linetype"] = _add_select_box(
                    key="tile_border_linetype",
                    label="Border linetype",
                    default="solid",
                    options=[
                        "solid",
                        "dashed",
                        "dotted",
                        "dotdash",
                        "longdash",
                        "twodash",
                    ],
                    get_setting_fn=get_uploaded_setting,
                    type_=str,
                )

            st.markdown("""---""")

            st.write("Sum tile settings:")

            col1, col2 = st.columns(2)
            with col1:
                output["sum_tile_palette"] = _add_select_box(
                    key="sum_tile_palette",
                    label="Color Palette",
                    default="Greens",
                    options=["Greens", "Oranges", "Greys", "Purples", "Reds", "Blues"],
                    get_setting_fn=get_uploaded_setting,
                    type_=str,
                )

            with col2:
                output["sum_tile_label"] = st.text_input(
                    "Label",
                    value=get_uploaded_setting(
                        key="sum_tile_label", default="Σ", type_=str
                    ),
                    key="sum_tiles_label",
                )

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
                output["show_zero_shading"] = st.checkbox(
                    "Add shading",
                    value=get_uploaded_setting(
                        key="show_zero_shading", default=True, type_=bool
                    ),
                )
            with col2:
                output["show_zero_text"] = st.checkbox(
                    "Show text",
                    value=get_uploaded_setting(
                        key="show_zero_text", default=False, type_=bool
                    ),
                    help="Whether to show counts, normalized (%), etc.",
                )
            with col3:
                output["show_zero_percentages"] = st.checkbox(
                    "Show row/column percentages",
                    value=get_uploaded_setting(
                        key="show_zero_percentages", default=False, type_=bool
                    ),
                    help="Only relevant when row/column percentages are enabled.",
                )

        if True:
            with st.expander("Fonts"):
                # Specify available settings and defaults per font
                font_types = {
                    "Top Font": {
                        "key_prefix": "font_top",
                        "description": "The big text in the middle (normalized (%) by default).",
                        "settings": {
                            "size": 4.3,  # 2.8
                            "color": "#000000",
                            "alpha": 1.0,
                            "bold": False,
                            "italic": False,
                        },
                    },
                    "Bottom Font": {
                        "key_prefix": "font_bottom",
                        "description": "The text just below the top font (counts by default).",
                        "settings": {
                            "size": 2.8,
                            "color": "#000000",
                            "alpha": 1.0,
                            "bold": False,
                            "italic": False,
                        },
                    },
                    "Percentages Font": {
                        "key_prefix": "font_percentage",
                        "description": "The row and column percentages.",
                        "settings": {
                            "size": 2.35,
                            "color": "#000000",
                            "alpha": 0.85,
                            "bold": False,
                            "italic": True,
                            "suffix": "%",
                            "prefix": "",
                        },
                    },
                    "Normalized (%)": {
                        "key_prefix": "font_normalized",
                        "description": "Special settings for the normalized (%) text.",
                        "settings": {"suffix": "%", "prefix": ""},
                    },
                    "Counts": {
                        "key_prefix": "font_counts",
                        "description": "Special settings for the counts text.",
                        "settings": {"suffix": "", "prefix": ""},
                    },
                }

                for font_type_title, font_type_spec in font_types.items():
                    st.markdown(f"**{font_type_title}**")
                    st.markdown(font_type_spec["description"])
                    num_cols = 3
                    font_settings = create_font_settings(
                        key_prefix=font_type_spec["key_prefix"],
                        get_setting_fn=get_uploaded_setting,
                        settings_to_get=list(font_type_spec["settings"].keys()),
                    )

                    for i, (setting_name, setting_widget) in enumerate(
                        font_settings.items()
                    ):
                        if i % num_cols == 0:
                            cols = st.columns(num_cols)
                        with cols[i % num_cols]:
                            default = font_type_spec["settings"][
                                setting_name[len(font_type_spec["key_prefix"]) + 1 :]
                            ]
                            output[setting_name] = setting_widget(
                                k=setting_name, d=default
                            )

                    if font_type_title != list(font_types.keys())[-1]:
                        st.markdown("""---""")

        st.markdown("""---""")

        if st.form_submit_button(label="Generate plot"):
            st.session_state["step"] = 3
            if (
                not output["show_sums"]
                or output["sum_tile_palette"] != output["palette"]
            ):
                # Save settings as json
                with open(design_settings_store_path, "w") as f:
                    json.dump(output, f)

        design_ready = False
        if st.session_state["step"] >= 3:
            design_ready = True
            if output["show_sums"] and output["sum_tile_palette"] == output["palette"]:
                st.error(
                    "The color palettes (background colors) "
                    "for the tiles and sum tiles are identical. "
                    "Please select a different color palette for "
                    "the sum tiles under **Tiles** >> *Sum tile settings*."
                )
                design_ready = False

    return output, design_ready, selected_classes, prob_of_class


# defaults: dict,
def create_font_settings(
    key_prefix: str, get_setting_fn: Callable, settings_to_get: List[str]
) -> Tuple[dict, dict]:
    # TODO: Defaults must be set based on font type! Also,
    # we probably need to allow not setting the argument so the
    # plotting function can handle the defaulting?
    def make_key(key):
        return f"{key_prefix}_{key}"

    font_settings = {
        make_key("color"): lambda k, d: st.color_picker(
            "Color",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=str),
        ),
        make_key("bold"): lambda k, d: st.checkbox(
            "Bold",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=bool),
        ),
        make_key("italic"): lambda k, d: st.checkbox(
            "Italic",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=bool),
        ),
        make_key("size"): lambda k, d: st.number_input(
            "Size",
            key=k,
            value=get_setting_fn(key=k, default=float(d), type_=float),
        ),
        make_key("nudge_x"): lambda k, d: st.number_input(
            "Nudge on x-axis",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=float),
        ),
        make_key("nudge_y"): lambda k, d: st.number_input(
            "Nudge on y-axis",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=float),
        ),
        make_key("alpha"): lambda k, d: st.slider(
            "Transparency",
            min_value=0.0,
            max_value=1.0,
            value=get_setting_fn(key=k, default=d, type_=float),
            step=0.01,
            key=k,
        ),
        make_key("prefix"): lambda k, d: st.text_input(
            "Prefix",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=str),
        ),
        make_key("suffix"): lambda k, d: st.text_input(
            "Suffix",
            key=k,
            value=get_setting_fn(key=k, default=d, type_=str),
        ),
    }

    # Filter settings
    font_settings = {
        k: v
        for k, v in font_settings.items()
        if f"{k[len(key_prefix)+1:]}" in settings_to_get
    }

    return font_settings
