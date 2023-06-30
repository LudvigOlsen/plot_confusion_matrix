from typing import List, Callable, Any, Tuple
import json
import streamlit as st
from PIL import Image

from components import add_toggle_horizontal, add_toggle_vertical
from text_sections import (
    design_text,
)
from templates import get_templates


def _add_select_box(
    key: str,
    label: str,
    default: Any,
    options: List[Any],
    get_setting_fn: Callable,
    type_=str,
    help=None,
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
        label, options=options, index=options.index(chosen_default), key=key, help=help
    )


templates = get_templates()


def select_settings():
    def reset_output_callback():
        st.session_state["selected_design_settings"].clear()
        if "uploaded_design_settings" in st.session_state:
            del st.session_state["uploaded_design_settings"]
        st.session_state["step"] = 2
        st.session_state["design_reset_mode"] = True
        st.session_state["num_resets"] += 1

    with st.expander("Templates"):
        col1, col2, _ = st.columns([1, 1, 2])
        with col1:
            # Find template with num classes closest to
            # the number of classes in the data
            templates_available_num_classes = sorted(
                set([d["num_classes"] for d in templates.values()])
            )
            closest_num_classes_distance = 99999
            closest_num_classes_idx = -1
            for idx, n in enumerate(templates_available_num_classes):
                distance = abs(n - len(st.session_state["classes"]))
                if distance < closest_num_classes_distance:
                    closest_num_classes_distance = distance
                    closest_num_classes_idx = idx

            n_classes = st.selectbox(
                "Number of classes",
                index=closest_num_classes_idx + 1,
                options=[-1] + templates_available_num_classes,
            )
        with col2:
            has_sums = add_toggle_vertical(
                label="With sum tiles",
                key="filter_sum_tiles",
                default=False,
                cols=[3, 5],
            )

        filtered_templates = {
            temp_name: temp
            for temp_name, temp in templates.items()
            if (n_classes == -1 or temp["num_classes"] == n_classes)
            and temp["sums"] == has_sums
        }

        num_cols = 3
        for i, (temp_name, template) in enumerate(filtered_templates.items()):
            if i % num_cols == 0:
                cols = st.columns(num_cols)
            temp_image = Image.open(f"template_resources/{template['image']}")
            with cols[i % 3]:
                st.image(
                    temp_image,
                    clamp=False,
                    channels="RGB",
                    output_format="auto",
                )
                _, col2, _ = st.columns([5, 6, 5])
                with col2:
                    if st.button(
                        "Select",
                        key=temp_name.replace(" ", "_"),
                        on_click=reset_output_callback,
                    ):
                        with open(
                            "template_resources/" + template["settings"],
                            "r",
                        ) as jfile:
                            st.session_state["uploaded_design_settings"] = json.load(
                                jfile
                            )

    with st.expander("Upload settings"):
        uploaded_settings_path = st.file_uploader(
            "Upload design settings", type=["json"]
        )
        if st.button(label="Apply settings", on_click=reset_output_callback):
            if uploaded_settings_path is not None:
                st.session_state["uploaded_design_settings"] = json.load(
                    uploaded_settings_path
                )

    _, col2, _ = st.columns([5, 2.5, 5])
    with col2:
        st.button("Reset design", on_click=reset_output_callback)


def design_section(
    num_classes,
    design_settings_store_path,
):
    st.session_state["selected_design_settings"] = {}

    st.markdown("---")
    design_text()
    select_settings()

    def get_uploaded_setting(key, default, type_=None, options=None):
        if (
            "uploaded_design_settings" in st.session_state
            and key in st.session_state["uploaded_design_settings"]
        ):
            out = st.session_state["uploaded_design_settings"][key]
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

    if st.session_state["design_reset_mode"]:
        if "form_placeholder" in st.session_state:
            st.session_state["form_placeholder"].empty()
        st.session_state["design_reset_mode"] = False

    st.session_state["form_placeholder"] = st.empty()
    with st.session_state["form_placeholder"].container():
        with st.form(key=f"settings_form_{st.session_state['num_resets']}"):
            col1, col2 = st.columns([4, 4])
            with col1:
                selected_classes = st.multiselect(
                    "Select classes (min=2, order is respected)",
                    options=st.session_state["classes"],
                    default=st.session_state["classes"],
                    help="Select the classes to create the confusion matrix for. "
                    "Any observation with either a target or prediction "
                    "of another class is excluded.",
                )
                # Reverse by default
                selected_classes.reverse()
            with col2:
                reverse_class_order = add_toggle_vertical(
                    label="Reverse class order",
                    key="reverse_order",
                    default=False,
                    cols=[2, 9],
                )

            # Color palette
            col1, col2, col3, col4 = st.columns([4, 4, 2, 2])
            with col1:
                st.session_state["selected_design_settings"][
                    "palette"
                ] = _add_select_box(
                    key="palette",
                    label="Color Palette",
                    default="Blues",
                    options=[
                        "Blues",
                        "Greens",
                        "Oranges",
                        "Greys",
                        "Purples",
                        "Reds",
                    ],
                    get_setting_fn=get_uploaded_setting,
                    type_=str,
                    help="Color of the tiles. Select a preset color palette or create a custom gradient. ",
                )
            with col2:
                st.session_state["selected_design_settings"][
                    "palette_use_custom"
                ] = add_toggle_vertical(
                    label="Use custom gradient",
                    key="custom_gradient",
                    default=get_uploaded_setting(
                        key="palette_use_custom",
                        default=False,
                        type_=bool,
                    ),
                )
            with col3:
                st.session_state["selected_design_settings"][
                    "palette_custom_low"
                ] = st.color_picker(
                    "Low color",
                    value=get_uploaded_setting(
                        key="palette_custom_low",
                        default="#B1F9E8",
                        type_=str,
                    ),
                )
            with col4:
                st.session_state["selected_design_settings"][
                    "palette_custom_high"
                ] = st.color_picker(
                    "High color",
                    value=get_uploaded_setting(
                        key="palette_custom_high",
                        default="#239895",
                        type_=str,
                    ),
                )

            # Ask for output parameters
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state["selected_design_settings"]["width"] = st.number_input(
                    "Width (px)",
                    value=get_uploaded_setting(
                        key="width", default=1200 + 100 * (num_classes - 2), type_=int
                    ),
                    step=50,
                )
            with col2:
                st.session_state["selected_design_settings"][
                    "height"
                ] = st.number_input(
                    "Height (px)",
                    value=get_uploaded_setting(
                        key="width",
                        default=1200 + 100 * (num_classes - 2),
                        type_=int,
                    ),
                    step=50,
                )
            with col3:
                st.session_state["selected_design_settings"]["dpi"] = st.number_input(
                    "DPI (scaling)",
                    value=get_uploaded_setting(key="dpi", default=320, type_=int),
                    step=10,
                    help="While the output file *currently* won't have this DPI, "
                    "the DPI setting affects scaling of elements. ",
                )

            st.write(" ")  # Slightly bigger gap between the two sections
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state["selected_design_settings"][
                    "show_counts"
                ] = add_toggle_vertical(
                    label="Show counts",
                    key="show_counts",
                    default=get_uploaded_setting(
                        key="show_counts", default=True, type_=bool
                    ),
                    cols=[2, 5],
                )
            with col2:
                st.session_state["selected_design_settings"][
                    "show_normalized"
                ] = add_toggle_vertical(
                    label="Show normalized (%)",
                    key="show_normalized",
                    default=get_uploaded_setting(
                        key="show_normalized", default=True, type_=bool
                    ),
                    cols=[2, 5],
                )
            with col3:
                st.session_state["selected_design_settings"][
                    "show_sums"
                ] = add_toggle_vertical(
                    label="Show sum tiles",
                    key="show_sum_tiles",
                    default=get_uploaded_setting(
                        key="show_sums", default=False, type_=bool
                    ),
                    cols=[2, 5],
                )
                # help="Show extra row and column with the "
                # "totals for that row/column.",

            st.markdown("""---""")
            st.markdown("**Advanced**:")

            with st.expander("Labels"):
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state["selected_design_settings"][
                        "x_label"
                    ] = st.text_input(
                        "x-axis",
                        value=get_uploaded_setting(
                            key="x_label", default="True Class", type_=str
                        ),
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "y_label"
                    ] = st.text_input(
                        "y-axis",
                        value=get_uploaded_setting(
                            key="y_label", default="Predicted Class", type_=str
                        ),
                    )

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state["selected_design_settings"][
                        "title_label"
                    ] = st.text_input(
                        "Title",
                        value=get_uploaded_setting(
                            key="title_label", default="", type_=str
                        ),
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "caption_label"
                    ] = st.text_input(
                        "Caption",
                        value=get_uploaded_setting(
                            key="caption_label", default="", type_=str
                        ),
                    )
                st.info(
                    "Note: When adding a title or caption, "
                    "you may need to adjust the height and "
                    "width of the plot as well."
                )

            with st.expander("Elements"):
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state["selected_design_settings"][
                        "rotate_y_text"
                    ] = add_toggle_horizontal(
                        label="Rotate y-axis text",
                        key="rotate_y_text",
                        default=get_uploaded_setting(
                            key="rotate_y_text", default=True, type_=bool
                        ),
                    )

                    st.session_state["selected_design_settings"][
                        "place_x_axis_above"
                    ] = add_toggle_horizontal(
                        label="Place x-axis on top",
                        default=get_uploaded_setting(
                            key="place_x_axis_above", default=True, type_=bool
                        ),
                        key="place_x_axis_above",
                    )
                    st.session_state["selected_design_settings"][
                        "counts_on_top"
                    ] = add_toggle_horizontal(
                        label="Counts on top",
                        default=get_uploaded_setting(
                            key="counts_on_top", default=False, type_=bool
                        ),
                        key="counts_on_top",
                    )
                    # Help note:
                    # "Whether to switch the positions of the counts and normalized counts (%). "
                    # "The counts become the big centralized numbers and the "
                    # "normalized counts go below with a smaller font size."

                with col2:
                    st.session_state["selected_design_settings"][
                        "num_digits"
                    ] = st.number_input(
                        "Digits",
                        value=get_uploaded_setting(
                            key="num_digits", default=2, type_=int
                        ),
                        help="Number of digits to round percentages to.",
                    )

                st.markdown("""---""")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("Row and column percentages:")
                    st.session_state["selected_design_settings"][
                        "show_row_percentages"
                    ] = add_toggle_horizontal(
                        label="Show row percentages",
                        default=get_uploaded_setting(
                            key="show_row_percentages",
                            default=num_classes < 6,
                            type_=bool,
                        ),
                        key="show_row_percentages",
                    )
                    st.session_state["selected_design_settings"][
                        "show_col_percentages"
                    ] = add_toggle_horizontal(
                        label="Show column percentages",
                        default=get_uploaded_setting(
                            key="show_col_percentages",
                            default=num_classes < 6,
                            type_=bool,
                        ),
                        key="show_col_percentages",
                    )
                    st.session_state["selected_design_settings"][
                        "show_arrows"
                    ] = add_toggle_horizontal(
                        label="Show arrows",
                        default=get_uploaded_setting(
                            key="show_arrows", default=True, type_=bool
                        ),
                        key="show_arrows",
                    )
                    st.session_state["selected_design_settings"][
                        "diag_percentages_only"
                    ] = add_toggle_horizontal(
                        label="Diagonal percentages only",
                        default=get_uploaded_setting(
                            key="diag_percentages_only",
                            default=False,
                            type_=bool,
                        ),
                        key="diag_percentages_only",
                    )
                with col2:
                    st.session_state["selected_design_settings"]["arrow_size"] = (
                        st.slider(
                            "Arrow size",
                            value=get_uploaded_setting(
                                key="arrow_size", default=0.048, type_=float
                            )
                            * 10,
                            min_value=0.03 * 10,
                            max_value=0.06 * 10,
                            step=0.001 * 10,
                        )
                        / 10
                    )
                    st.session_state["selected_design_settings"][
                        "arrow_nudge_from_text"
                    ] = (
                        st.slider(
                            "Arrow nudge from text",
                            value=get_uploaded_setting(
                                key="arrow_nudge_from_text",
                                default=0.065,
                                type_=float,
                            )
                            * 10,
                            min_value=0.00,
                            max_value=0.1 * 10,
                            step=0.001 * 10,
                        )
                        / 10
                    )

            with st.expander("Tiles"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.session_state["selected_design_settings"][
                        "intensity_by"
                    ] = _add_select_box(
                        key="intensity_by",
                        label="Intensity based on",
                        default="Counts",
                        options=[
                            "Counts",
                            "Normalized (%)",
                            "Log Counts",
                            "Log2 Counts",
                            "Log10 Counts",
                            "Arcsinh Counts",
                        ],
                        get_setting_fn=get_uploaded_setting,
                        type_=str,
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "darkness"
                    ] = st.slider(
                        "Darkness",
                        min_value=0.0,
                        max_value=1.0,
                        value=get_uploaded_setting(
                            key="darkness", default=0.8, type_=float
                        ),
                        step=0.01,
                        help="How dark the darkest colors should be, between 0 and 1, where 1 is darkest.",
                    )
                with col3:
                    st.session_state["selected_design_settings"][
                        "amount_3d_effect"
                    ] = st.slider(
                        "3D effect",
                        min_value=0,
                        max_value=6,
                        value=get_uploaded_setting(
                            key="amount_3d_effect", default=1, type_=int
                        ),
                        step=1,
                        help="Amount of 3D effect on the tiles. 0 turns off the 3D effect. "
                        "1 or 2 are good defaults. The 3D effect helps separate tiles with "
                        "the same color intensity.",
                    )

                col1, col2, col3, col4 = st.columns([4, 5, 5, 6])
                with col1:
                    st.session_state["selected_design_settings"][
                        "set_intensity_lims"
                    ] = add_toggle_vertical(
                        label="Set intensity range",
                        default=False,
                        key="set_intensity_lims",
                        cols=[5, 1],
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "intensity_min"
                    ] = st.number_input(
                        "Intensity min.",
                        value=get_uploaded_setting(
                            key="intensity_min", default=0.0, type_=float
                        ),
                        help="The value to consider the minimum intensity. "
                        "The values are based on the `Intensity based on` selection.",
                    )
                with col3:
                    st.session_state["selected_design_settings"][
                        "intensity_max"
                    ] = st.number_input(
                        "Intensity max.",
                        value=get_uploaded_setting(
                            key="intensity_max", default=0.0, type_=float
                        ),
                        help="The value to consider the maximum intensity. "
                        "The values are based on the `Intensity based on` selection.",
                    )
                with col4:
                    st.session_state["selected_design_settings"][
                        "intensity_beyond_lims"
                    ] = _add_select_box(
                        key="intensity_beyond_lims",
                        label="Out-of-range values",
                        default="truncate",
                        options=["truncate", "grey"],
                        get_setting_fn=get_uploaded_setting,
                        type_=str,
                        help="What to do with counts/percentages outside of the specified intensity range.",
                    )

                st.markdown("""---""")

                st.session_state["selected_design_settings"][
                    "show_tile_border"
                ] = add_toggle_horizontal(
                    label="Add tile borders",
                    default=get_uploaded_setting(
                        key="show_tile_border", default=False, type_=bool
                    ),
                    key="show_tile_border",
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.session_state["selected_design_settings"][
                        "tile_border_color"
                    ] = st.color_picker(
                        "Border color",
                        value=get_uploaded_setting(
                            key="tile_border_color",
                            default="#000000",
                            type_=str,
                        ),
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "tile_border_size"
                    ] = st.slider(
                        "Border size",
                        min_value=0.0,
                        max_value=3.0,
                        value=get_uploaded_setting(
                            key="tile_border_size", default=0.1, type_=float
                        ),
                        step=0.01,
                    )
                with col3:
                    st.session_state["selected_design_settings"][
                        "tile_border_linetype"
                    ] = _add_select_box(
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

                # Color palette
                col1, col2, col3, col4 = st.columns([4, 4, 2, 2])
                with col1:
                    st.session_state["selected_design_settings"][
                        "sum_tile_palette"
                    ] = _add_select_box(
                        key="sum_tile_palette",
                        label="Color Palette",
                        default="Greens",
                        options=[
                            "Greens",
                            "Oranges",
                            "Greys",
                            "Purples",
                            "Reds",
                            "Blues",
                        ],
                        get_setting_fn=get_uploaded_setting,
                        type_=str,
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "sum_tile_palette_use_custom"
                    ] = add_toggle_vertical(
                        label="Use custom gradient",
                        key="sum_tile_palette_use_custom",
                        default=get_uploaded_setting(
                            key="sum_tile_palette_use_custom", default=False, type_=bool
                        ),
                    )
                with col3:
                    st.session_state["selected_design_settings"][
                        "sum_tile_palette_custom_low"
                    ] = st.color_picker(
                        "Low color",
                        key="sum_tile_palette_custom_low",
                        value=get_uploaded_setting(
                            key="sum_tile_palette_custom_low",
                            default="#e9e1fc",
                            type_=str,
                        ),
                    )
                with col4:
                    st.session_state["selected_design_settings"][
                        "sum_tile_palette_custom_high"
                    ] = st.color_picker(
                        "High color",
                        key="sum_tile_palette_custom_high",
                        value=get_uploaded_setting(
                            key="sum_tile_palette_custom_high",
                            default="#BE94E6",
                            type_=str,
                        ),
                    )

                col1, col2 = st.columns(2)
                with col1:
                    st.session_state["selected_design_settings"][
                        "sum_tile_label"
                    ] = st.text_input(
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
                    st.session_state["selected_design_settings"][
                        "show_zero_shading"
                    ] = add_toggle_vertical(
                        label="Add shading",
                        default=get_uploaded_setting(
                            key="show_zero_shading", default=True, type_=bool
                        ),
                        key="show_zero_shading",
                    )
                with col2:
                    st.session_state["selected_design_settings"][
                        "show_zero_text"
                    ] = add_toggle_vertical(
                        label="Show main text",
                        default=get_uploaded_setting(
                            key="show_zero_text", default=False, type_=bool
                        ),
                        key="show_zero_text",
                    )
                with col3:
                    st.session_state["selected_design_settings"][
                        "show_zero_percentages"
                    ] = add_toggle_vertical(
                        label="Show row/column percentages",
                        default=get_uploaded_setting(
                            key="show_zero_percentages",
                            default=False,
                            type_=bool,
                        ),
                        key="show_zero_percentages",
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
                                    setting_name[
                                        len(font_type_spec["key_prefix"]) + 1 :
                                    ]
                                ]
                                st.session_state["selected_design_settings"][
                                    setting_name
                                ] = setting_widget(k=setting_name, d=default)

                        if font_type_title != list(font_types.keys())[-1]:
                            st.markdown("""---""")

            st.markdown("""---""")

            if st.form_submit_button(label="Generate plot"):
                st.session_state["step"] = 3
                if (
                    not st.session_state["selected_design_settings"]["show_sums"]
                    or st.session_state["selected_design_settings"]["sum_tile_palette"]
                    != st.session_state["selected_design_settings"]["palette"]
                ):
                    # Save settings as json
                    with open(design_settings_store_path, "w") as f:
                        json.dump(st.session_state["selected_design_settings"], f)
                if not st.session_state["selected_design_settings"][
                    "place_x_axis_above"
                ]:
                    selected_classes.reverse()
                if reverse_class_order:
                    selected_classes.reverse()

    design_ready = False
    if st.session_state["step"] >= 3:
        design_ready = True
        if (
            st.session_state["selected_design_settings"]["show_sums"]
            and st.session_state["selected_design_settings"]["sum_tile_palette"]
            == st.session_state["selected_design_settings"]["palette"]
        ):
            st.error(
                "The color palettes (background colors) "
                "for the tiles and sum tiles are identical. "
                "Please select a different color palette for "
                "the sum tiles under **Tiles** >> *Sum tile settings*."
            )
            design_ready = False
        if (
            st.session_state["selected_design_settings"]["set_intensity_lims"]
            and not st.session_state["selected_design_settings"]["intensity_max"]
            > st.session_state["selected_design_settings"]["intensity_min"]
        ):
            st.error(
                "When specifying an intensity range, "
                "the maximum value must be greater than the minimum value."
            )
            design_ready = False
        if len(selected_classes) < 2:
            st.error("At least 2 classes must be selected.")
            design_ready = False

    return design_ready, selected_classes


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
        make_key("bold"): lambda k, d: add_toggle_horizontal(
            label="Bold",
            key=k,
            default=get_setting_fn(key=k, default=d, type_=bool),
        ),
        make_key("italic"): lambda k, d: add_toggle_horizontal(
            label="Italic",
            key=k,
            default=get_setting_fn(key=k, default=d, type_=bool),
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
