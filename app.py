"""
App for plotting confusion matrix with `cvms::plot_confusion_matrix()`.

TODO:
- IMPORTANT! Allow specifying which class probabilities are of! (See plot prob_of_class)
- Allow setting threshold - manual, max J, spec/sens
- Add bg box around confusion matrix plot as text dissappears on dark mode!
- ggsave does not use dpi??
- allow svg, pdf?
- entered count -> counts (upload as well)
- Add full reset button (empty cache on different files)

"""

import pathlib
import tempfile
from PIL import Image
import streamlit as st  # Import last
import pandas as pd
from pandas.api.types import is_float_dtype
from itertools import combinations
from collections import OrderedDict

from utils import call_subprocess, clean_string_for_non_alphanumerics
from data import read_data, read_data_cached, DownloadHeader, generate_data
from text_sections import (
    intro_text,
    columns_text,
    upload_predictions_text,
    upload_counts_text,
    generate_data_text,
    design_text,
    enter_count_data_text,
)


# Create temporary directory


@st.cache_resource
def set_tmp_dir():
    """
    Must cache to avoid regenerating!
    Must be the same throughout the iterations!
    """
    temp_dir = tempfile.TemporaryDirectory()
    return temp_dir, temp_dir.name


temp_dir, temp_dir_path = set_tmp_dir()
gen_data_store_path = pathlib.Path(f"{temp_dir_path}/generated_data.csv")
data_store_path = pathlib.Path(f"{temp_dir_path}/data.csv")
conf_mat_path = pathlib.Path(f"{temp_dir_path}/confusion_matrix.png")


def input_choice_callback():
    """
    Resets steps to 0.
    Used when switching between input methods.
    """
    st.session_state["step"] = 0
    st.session_state["input_type"] = None

    # Remove old tmp files
    if gen_data_store_path.exists():
        gen_data_store_path.unlink()
    if data_store_path.exists():
        data_store_path.unlink()
    if conf_mat_path.exists():
        conf_mat_path.unlink()


# Text
intro_text()

# Start step counter
# Required to make dependent forms work
if st.session_state.get("step") is None:
    st.session_state["step"] = 0

input_choice = st.radio(
    label="Input",
    options=["Upload predictions", "Upload counts", "Generate", "Enter counts"],
    index=0,
    horizontal=True,
    on_change=input_choice_callback,
)

# Check whether the expected output
if st.session_state.get("input_type") is None:
    if input_choice in ["Upload predictions", "Generate"]:
        st.session_state["input_type"] = "data"
    else:
        st.session_state["input_type"] = "counts"

# Load data
if input_choice == "Upload predictions":
    with st.form(key="data_form"):
        upload_predictions_text()
        data_path = st.file_uploader("Upload a dataset", type=["csv"])
        if st.form_submit_button(label="Use data"):
            if data_path:
                st.session_state["step"] = 1
            else:
                st.session_state["step"] = 0
                st.markdown("Please upload a file first (or **generate** some random data to try the function).")

    if st.session_state["step"] >= 1:
        # Read and store (tmp) data
        df = read_data_cached(data_path)
        with st.form(key="column_form"):
            columns_text()
            target_col = st.selectbox("Targets column", options=list(df.columns))
            prediction_col = st.selectbox(
                "Predictions column", options=list(df.columns)
            )

            if st.form_submit_button(label="Set columns"):
                st.session_state["step"] = 2

# Load data
elif input_choice == "Upload counts":
    with st.form(key="data_form"):
        upload_counts_text()
        data_path = st.file_uploader("Upload a dataset", type=["csv"])
        if st.form_submit_button(label="Use data"):
            if data_path:
                st.session_state["step"] = 1
            else:
                st.session_state["step"] = 0
                st.write("Please upload a file first.")

    if st.session_state["step"] >= 1:
        # Read and store (tmp) data
        df = read_data_cached(data_path)
        with st.form(key="column_form"):
            columns_text()
            target_col = st.selectbox("Targets column", options=list(df.columns))
            prediction_col = st.selectbox(
                "Predictions column", options=list(df.columns)
            )
            n_col = st.selectbox(
                "Counts column", options=list(df.columns)
            )

            if st.form_submit_button(label="Set columns"):
                st.session_state["step"] = 2


# Generate data
elif input_choice == "Generate":

    def reset_generation_callback():
        p = pathlib.Path(gen_data_store_path)
        if p.exists():
            p.unlink()

    with st.form(key="generate_form"):
        generate_data_text()
        col1, col2, col3 = st.columns(3)
        with col1:
            num_classes = st.number_input(
                "# Classes",
                value=3,
                min_value=2,
                help="Number of classes to generate data for.",
            )
        with col2:
            num_observations = st.number_input(
                "# Observations",
                value=30,
                min_value=2,
                max_value=10000,
                help="Number of observations to generate data for.",
            )
        with col3:
            seed = st.number_input("Random Seed", value=42, min_value=0)
        if st.form_submit_button(
            label="Generate data", on_click=reset_generation_callback
        ):
            st.session_state["step"] = 2

    if st.session_state["step"] >= 2:
        generate_data(
            out_path=gen_data_store_path,
            num_classes=num_classes,
            num_observations=num_observations,
            seed=seed,
        )
        df = read_data(gen_data_store_path)
        target_col = "Target"
        prediction_col = "Predicted Class"

elif input_choice == "Enter counts":

    def repopulate_matrix_callback():
        if "entered_counts" not in st.session_state:
            if "entered_counts" in st.session_state:
                st.session_state.pop("entered_counts")

    with st.form(key="enter_classes_form"):
        enter_count_data_text()
        classes_joined = st.text_input("Classes (comma-separated)")

        if st.form_submit_button(
            label="Populate matrix", on_click=repopulate_matrix_callback
        ):
            # Extract class names from comma-separated list
            st.session_state["classes"] = [
                clean_string_for_non_alphanumerics(s) for s in classes_joined.split(",")
            ]

            # Calculate all pairs of predictions and targets
            all_pairs = list(combinations(st.session_state["classes"], 2))
            all_pairs += [(pair[1], pair[0]) for pair in all_pairs]
            all_pairs += [(c, c) for c in st.session_state["classes"]]

            # Prepopulate the matrix
            st.session_state["entered_counts"] = pd.DataFrame(
                all_pairs, columns=["Target", "Prediction"]
            )

            st.session_state["step"] = 1

    if st.session_state["step"] >= 1:
        with st.form(key="enter_counts_form"):
            st.write("Fill in the counts for `N(Target, Prediction)` pairs.")
            count_input_fields = OrderedDict()

            num_cols = 3
            cols = st.columns(num_cols)
            for i, (targ, pred) in enumerate(
                zip(
                    st.session_state["entered_counts"]["Target"],
                    st.session_state["entered_counts"]["Prediction"],
                )
            ):
                count_input_fields[f"{targ}____{pred}"] = cols[
                    i % num_cols
                ].number_input(f"N({targ}, {pred})", step=1)

            if st.form_submit_button(
                label="Generate data",
            ):
                st.session_state["entered_counts"]["N"] = [
                    int(val) for val in count_input_fields.values()
                ]
                st.session_state["step"] = 2

    if st.session_state["step"] >= 2:
        DownloadHeader.header_and_data_download(
            "Entered counts",
            data=st.session_state["entered_counts"],
            file_name="Confusion_Matrix_Counts.csv",
            help="Download counts",
        )
        st.write(st.session_state["entered_counts"])

        target_col = "Target"
        prediction_col = "Prediction"
        n_col = "N"

if st.session_state["step"] >= 2:
    if st.session_state["input_type"] == "data":
        # Remove unused columns
        df = df.loc[:, [target_col, prediction_col]]

        # Ensure targets are strings
        df[target_col] = df[target_col].astype(str)
        df[target_col] = df[target_col].apply(lambda x: x.replace(" ", "_"))

        # Save to tmp directory to allow reading in R script
        df.to_csv(data_store_path)

        # Extract unique classes
        st.session_state["classes"] = sorted([str(c) for c in df[target_col].unique()])

        predictions_are_probabilities = is_float_dtype(df[prediction_col])
        if predictions_are_probabilities and len(st.session_state["classes"]) != 2:
            st.error(
                "Predictions can only be probabilities in binary classification. "
                f"Got {len(st.session_state['classes'])} classes."
            )

        st.subheader("The Data")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            st.write(df.head(5))
            st.write(f"{df.shape} (first 5 rows).")

    else:
        st.session_state["entered_counts"].to_csv(data_store_path)

    # Check the number of classes
    num_classes = len(st.session_state["classes"])
    print(st.session_state["classes"])
    if num_classes < 2:
        # TODO Handle better than throwing error?
        raise ValueError(
            "Uploaded data must contain 2 or more classes in `Targets column`. "
            f"Got {num_classes} target classes."
        )

    with st.form(key="settings_form"):
        design_text()
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
            if st.session_state["input_type"] == "data" and predictions_are_probabilities:
                prob_of_class = st.selectbox(
                    "Probabilities are of (not working)",
                    options=st.session_state["classes"],
                    index=1,
                )
            else:
                prob_of_class = None

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

        col1, col2, col3 = st.columns(3)
        with col1:
            counts_on_top = st.checkbox(
                "Counts on top (not working)",
                help="Whether to switch the positions of the counts and normalized counts (%). "
                "That is, the counts become the big centralized numbers and the "
                "normalized counts go below with a smaller font size.",
            )
        with col2:
            diag_percentages_only = st.checkbox("Diagonal row/column percentages only")
        with col3:
            num_digits = st.number_input(
                "Digits", value=2, help="Number of digits to round percentages to."
            )

        element_flags = [
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

        palette = st.selectbox(
            "Color Palette",
            options=["Blues", "Greens", "Oranges", "Greys", "Purples", "Reds"],
        )

        # Ask for output parameters
        # TODO: Set default based on number of classes and sum tiles
        col1, col2, col3 = st.columns(3)
        with col1:
            width = st.number_input("Width (px)", value=1200 + 100 * (num_classes - 2))
        with col2:
            height = st.number_input(
                "Height (px)", value=1200 + 100 * (num_classes - 2)
            )
        with col3:
            dpi = st.number_input("DPI (not working)", value=320)

        if st.form_submit_button(label="Apply"):
            st.session_state["step"] = 3

    if st.session_state["step"] >= 3:
        plotting_args = [
            "--data_path",
            f"'{data_store_path}'",
            "--out_path",
            f"'{conf_mat_path}'",
            "--target_col",
            f"'{target_col}'",
            "--prediction_col",
            f"'{prediction_col}'",
            "--width",
            f"{width}",
            "--height",
            f"{height}",
            "--dpi",
            f"{dpi}",
            "--classes",
            f"{','.join(selected_classes)}",
            "--digits",
            f"{num_digits}",
            "--palette",
            f"{palette}",
        ]

        if st.session_state["input_type"] == "counts":
            # The input data are counts
            plotting_args += ["--n_col", f"{n_col}", "--data_are_counts"]

        plotting_args += element_flags

        plotting_args = " ".join(plotting_args)

        call_subprocess(
            f"Rscript plot.R {plotting_args}",
            message="Plotting script",
            return_output=True,
            encoding="UTF-8",
        )

        DownloadHeader.header_and_image_download(
            "The confusion matrix plot", filepath=conf_mat_path
        )
        col1, col2, col3 = st.columns([2, 8, 2])
        with col2:
            image = Image.open(conf_mat_path)
            st.image(
                image,
                caption="Confusion Matrix",
                # width=500,
                use_column_width=None,
                clamp=False,
                channels="RGB",
                output_format="auto",
            )

        # evaluation = dplyr.select(
        #     evaluation,
        #     "Balanced Accuracy",
        #     "Accuracy",
        #     "F1",
        #     "Sensitivity",
        #     "Specificity",
        #     "Pos Pred Value",
        #     "Neg Pred Value",
        #     "AUC",
        #     "Kappa",
        #     "MCC",
        # )
        # evaluation_py = ro.conversion.rpy2py(evaluation)
        # st.write(evaluation_py)

    # confusion_matrix_py = ro.conversion.rpy2py(confusion_matrix)
    # st.write(confusion_matrix_py)

    # evaluation = dplyr.select(
    #     evaluation,
    #     "Balanced Accuracy",
    #     "Accuracy",
    #     "F1",
    #     "Sensitivity",
    #     "Specificity",
    #     "Pos Pred Value",
    #     "Neg Pred Value",
    #     "AUC",
    #     "Kappa",
    #     "MCC",
    # )
    # evaluation_py = ro.conversion.rpy2py(evaluation)
    # st.write(evaluation_py)

    # temp_dir.cleanup()

else:
    st.write("Please upload data.")


#   target_col = "Target",
#   prediction_col = "Prediction",
#   counts_col = "N",
#   class_order = NULL,
#   add_sums = FALSE,
#   add_counts = TRUE,
#   add_normalized = TRUE,
#   add_row_percentages = TRUE,
#   add_col_percentages = TRUE,
#   diag_percentages_only = FALSE,
#   rm_zero_percentages = TRUE,
#   rm_zero_text = TRUE,
#   add_zero_shading = TRUE,
#   add_arrows = TRUE,
#   counts_on_top = FALSE,
#   palette = "Blues",
#   intensity_by = "counts",
#   theme_fn = ggplot2::theme_minimal,
#   place_x_axis_above = TRUE,
#   rotate_y_text = TRUE,
#   digits = 1,
#   font_counts = font(),
#   font_normalized = font(),
#   font_row_percentages = font(),
#   font_col_percentages = font(),
#   arrow_size = 0.048,
#   arrow_nudge_from_text = 0.065,
#   tile_border_color = NA,
#   tile_border_size = 0.1,
#   tile_border_linetype = "solid",
#   sums_settings = sum_tile_settings(),
#   darkness = 0.8
# )
