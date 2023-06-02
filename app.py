"""
App for plotting confusion matrix with `cvms::plot_confusion_matrix()`.

TODO:
- IMPORTANT! Allow specifying which class probabilities are of! (See plot prob_of_class)
- IMPORTANT! Use json/txt file to pass settings to r instead?
- IMPORTANT! Allow saving and uploading design settings - so many of them
  that one shouldn't have to enter all the changes for every plot
  when making multiple at a time!
- Allow setting threshold - manual, max J, spec/sens
- Add bg box around confusion matrix plot as text dissappears on dark mode!
- ggsave does not use dpi??
- allow svg, pdf?
- entered count -> counts (upload as well)
- Add full reset button (empty cache on different files) - callback?
- Handle <2 classes in design box (add st.error)
- Handle classes with spaces in them?
- Add option to change zero-tile background (e.g. to black for black backgrounds)

NOTE: 


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
from design import design_section
from text_sections import (
    intro_text,
    columns_text,
    upload_predictions_text,
    upload_counts_text,
    generate_data_text,
    enter_count_data_text,
)

st.markdown(
    """
<style>
.small-font {
    font-size:0.85em !important;
}
</style>
""",
    unsafe_allow_html=True,
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
design_settings_store_path = pathlib.Path(f"{temp_dir_path}/design_settings.json")
conf_mat_path = pathlib.Path(f"{temp_dir_path}/confusion_matrix.png")


def input_choice_callback():
    """
    Resets steps to 0.
    Used when switching between input methods.
    """
    st.session_state["step"] = 0
    st.session_state["input_type"] = None

    to_delete = ["classes", "count_data"]
    for key in to_delete:
        if key in st.session_state:
            st.session_state.pop(key)

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
                st.markdown(
                    "Please upload a file first (or **generate** some random data to try the function)."
                )

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
        data_path = st.file_uploader("Upload your counts", type=["csv"])
        if st.form_submit_button(label="Use counts"):
            if data_path:
                st.session_state["step"] = 1
            else:
                st.session_state["step"] = 0
                st.write("Please upload a file first.")

    if st.session_state["step"] >= 1:
        # Read and store (tmp) data
        st.session_state["count_data"] = read_data_cached(data_path)
        with st.form(key="column_form"):
            columns_text()
            target_col = st.selectbox(
                "Targets column", options=list(st.session_state["count_data"].columns)
            )
            prediction_col = st.selectbox(
                "Predictions column",
                options=list(st.session_state["count_data"].columns),
            )
            n_col = st.selectbox(
                "Counts column", options=list(st.session_state["count_data"].columns)
            )

            if st.form_submit_button(label="Set columns"):
                st.session_state["step"] = 2
                st.session_state["classes"] = sorted(
                    [
                        str(c)
                        for c in st.session_state["count_data"][target_col].unique()
                    ]
                )

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
        if "count_data" not in st.session_state:
            if "count_data" in st.session_state:
                st.session_state.pop("count_data")

    with st.form(key="enter_classes_form"):
        enter_count_data_text()
        classes_joined = st.text_input("Classes (comma-separated)")

        if st.form_submit_button(
            label="Populate matrix", on_click=repopulate_matrix_callback
        ):
            # Extract class names from comma-separated list
            # TODO: Allow white space in classes?
            st.session_state["classes"] = [
                clean_string_for_non_alphanumerics(s) for s in classes_joined.split(",")
            ]

            # Calculate all pairs of predictions and targets
            all_pairs = list(combinations(st.session_state["classes"], 2))
            all_pairs += [(pair[1], pair[0]) for pair in all_pairs]
            all_pairs += [(c, c) for c in st.session_state["classes"]]

            # Prepopulate the matrix
            st.session_state["count_data"] = pd.DataFrame(
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
                    st.session_state["count_data"]["Target"],
                    st.session_state["count_data"]["Prediction"],
                )
            ):
                count_input_fields[f"{targ}____{pred}"] = cols[
                    i % num_cols
                ].number_input(f"N({targ}, {pred})", step=1)

            if st.form_submit_button(
                label="Generate data",
            ):
                st.session_state["count_data"]["N"] = [
                    int(val) for val in count_input_fields.values()
                ]
                st.session_state["step"] = 2

    if st.session_state["step"] >= 2:
        DownloadHeader.header_and_data_download(
            "Entered counts",
            data=st.session_state["count_data"],
            file_name="confusion_matrix_counts.csv",
            help="Download counts",
            col_sizes=[10, 2],
        )
        col1, col2, col3 = st.columns([4, 5, 4])
        with col2:
            st.write(st.session_state["count_data"])
            st.write(f"{st.session_state['count_data'].shape}")

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
            st.write(f"{df.shape} (Showing first 5 rows)")

    else:
        predictions_are_probabilities = False
        st.session_state["count_data"].to_csv(data_store_path)

    # Check the number of classes
    num_classes = len(st.session_state["classes"])
    if num_classes < 2:
        # TODO Handle better than throwing error?
        raise ValueError(
            "Uploaded data must contain 2 or more classes in `Targets column`. "
            f"Got {num_classes} target classes."
        )

    # Section for specifying design settings

    design_settings, design_ready, selected_classes, prob_of_class = design_section(
        num_classes=num_classes,
        predictions_are_probabilities=predictions_are_probabilities,
        design_settings_store_path=design_settings_store_path,
    )

    # design_ready tells us whether to proceed or wait
    # for user to fix issues
    if st.session_state["step"] >= 3 and design_ready:
        DownloadHeader.centered_json_download(
            data=design_settings,
            file_name="design_settings.json",
            label="Download design settings",
            help="Download the design settings to allow reusing settings in future plots.",
        )

        st.markdown("---")

        plotting_args = [
            "--data_path",
            f"'{data_store_path}'",
            "--out_path",
            f"'{conf_mat_path}'",
            "--settings_path",
            f"'{design_settings_store_path}'",
            "--target_col",
            f"'{target_col}'",
            "--prediction_col",
            f"'{prediction_col}'",
            "--classes",
            f"{','.join(selected_classes)}",
        ]

        if st.session_state["input_type"] == "counts":
            # The input data are counts
            plotting_args += ["--n_col", f"{n_col}", "--data_are_counts"]

        plotting_args = " ".join(plotting_args)

        call_subprocess(
            f"Rscript plot.R {plotting_args}",
            message="Plotting script",
            return_output=True,
            encoding="UTF-8",
        )

        DownloadHeader.header_and_image_download(
            "", filepath=conf_mat_path, label="Download Plot"
        )
        col1, col2, col3 = st.columns([2, 8, 2])
        with col2:
            image = Image.open(conf_mat_path)
            st.image(
                image,
                caption="Confusion Matrix",
                clamp=False,
                channels="RGB",
                output_format="auto",
            )

else:
    st.write("Please upload data.")

# Spacing
for _ in range(5):
    st.write(" ")

st.markdown("---")
st.write()
col1, col2, col3, _ = st.columns([6, 3, 3, 3])
with col1:
    st.write("Developed by [Ludvig Renbo Olsen](http://ludvigolsen.dk)")
with col2:
    st.markdown("[Report issues](https://github.com/LudvigOlsen/cvms_plot_app/issues)")
with col3:
    st.markdown("[Source code](https://github.com/LudvigOlsen/cvms_plot_app/)")
