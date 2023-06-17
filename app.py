"""
App for plotting confusion matrix with `cvms::plot_confusion_matrix()`.

"""

import pathlib
import tempfile
from PIL import Image
import streamlit as st  # Import last
import pandas as pd
from pandas.api.types import is_float_dtype
from itertools import combinations

from utils import (
    call_subprocess,
    clean_string_for_non_alphanumerics,
    clean_str_column,
    min_max_scale_list,
)
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
    st.session_state["num_resets"] = 0

    to_delete = ["classes", "count_data", "uploaded_design_settings"]
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

    # Allows design settings to show
    st.session_state["design_reset_mode"] = False


# Text
intro_text()

# Start step counter
# Required to make dependent forms work
if st.session_state.get("step") is None:
    st.session_state["step"] = 0

input_choice = st.radio(
    label="Input Choice",
    label_visibility="hidden",
    key="InputChoice",
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
            sub_col = st.selectbox(
                "Sub column",
                options=["--"] + list(st.session_state["count_data"].columns),
                help="Optional! This column will replace the bottom text in the middle of the tiles.",
            )

            if st.form_submit_button(label="Set columns"):
                st.session_state["step"] = 2

        if st.session_state["step"] >= 2:
            # Ensure targets and predictions are clean strings
            st.session_state["count_data"][target_col] = clean_str_column(
                st.session_state["count_data"][target_col]
            )
            st.session_state["count_data"][prediction_col] = clean_str_column(
                st.session_state["count_data"][prediction_col]
            )
            st.session_state["classes"] = sorted(
                [c for c in st.session_state["count_data"][target_col].unique()]
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
            st.session_state["count_data"]["Sub"] = ""
            st.session_state["count_data"]["N"] = 0

            st.session_state["step"] = 1

    if st.session_state["step"] >= 1:
        with st.form(key="enter_counts_form"):
            st.write(
                "Fill in the counts by pressing each cell in the `N` column and inputting the counts. "
            )
            st.markdown(
                "(**Optional**) If you wish to specify the bottom text in the middle of the tiles, "
                "you can fill in the `Sub` column.",
                help="The `sub` column text replaces the bottom text (counts by default). "
                "The design settings for the replaced element (e.g. counts) are used for this text instead.",
            )
            st.info(
                "Note: Please click outside the cell before "
                "pressing `Generate data` to register your change."
            )

            new_counts = st.data_editor(
                st.session_state["count_data"],
                hide_index=True,
                column_config={
                    "Target": st.column_config.TextColumn(disabled=True),
                    "Prediction": st.column_config.TextColumn(disabled=True),
                    "Sub": st.column_config.TextColumn(
                        help="This text replaces the bottom text (in the middle of the tiles). "
                        "By default, the counts are replaced. "
                        "Note that the settings for this text are named "
                        "by the text element it replaces (e.g. **Fonts**>>*Counts*)."
                    ),
                    "N": st.column_config.NumberColumn(
                        disabled=False, min_value=0, step=1
                    ),
                },
            )

            if st.form_submit_button(
                label="Generate data",
            ):
                st.session_state["count_data"] = new_counts
                st.session_state["step"] = 2

    if st.session_state["step"] >= 2:
        DownloadHeader.header_and_data_download(
            "",
            data=st.session_state["count_data"],
            file_name="confusion_matrix_counts.csv",
            label="Download counts",
            help="Download counts",
            col_sizes=[10, 3],
        )
        target_col = "Target"
        prediction_col = "Prediction"
        n_col = "N"
        sub_col = "Sub" if any(st.session_state["count_data"]["Sub"]) else None


if st.session_state["step"] >= 2:
    data_is_ready = False
    if st.session_state["input_type"] == "data":
        # Remove unused columns
        df = df.loc[:, [target_col, prediction_col]]

        predictions_are_probabilities = is_float_dtype(df[prediction_col])
        if predictions_are_probabilities:
            st.error(
                "Predictions should be the predicted classes - not probabilities. "
            )
            data_is_ready = False
        else:
            data_is_ready = True

        if data_is_ready:
            # Ensure targets and predictions are clean strings
            df[target_col] = clean_str_column(df[target_col])
            df[prediction_col] = clean_str_column(df[prediction_col])

            # Save to tmp directory to allow reading in R script
            df.to_csv(data_store_path, index=False)

            # Extract unique classes
            st.session_state["classes"] = sorted(
                [str(c) for c in df[target_col].unique()]
            )

            st.subheader("The data")
            col1, col2, col3 = st.columns([3, 2, 3])
            with col2:
                st.dataframe(df.head(5), hide_index=True)
                st.write(f"{df.shape} (Showing first 5 rows)")

    else:
        count_data_clean = st.session_state["count_data"].copy()
        if not any(count_data_clean["Sub"]):
            del count_data_clean["Sub"]
        count_data_clean.to_csv(data_store_path, index=False)
        data_is_ready = True

    if data_is_ready:
        # Check the number of classes
        num_classes = len(st.session_state["classes"])
        if num_classes < 2:
            # TODO Handle better than throwing error?
            raise ValueError(
                "Uploaded data must contain 2 or more classes in `Targets column`. "
                f"Got {num_classes} target classes."
            )

        # Section for specifying design settings

        design_ready, selected_classes = design_section(
            num_classes=num_classes,
            design_settings_store_path=design_settings_store_path,
        )

        # design_ready tells us whether to proceed or wait
        # for user to fix issues
        if st.session_state["step"] >= 3 and design_ready:
            DownloadHeader.centered_json_download(
                data=st.session_state["selected_design_settings"],
                file_name="design_settings.json",
                label="Download design settings",
                help="Download the design settings to allow reusing settings in future plots.",
            )

            st.markdown("---")

            selected_classes_string = ",".join([f"'{c}'" for c in selected_classes])

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
                f"{selected_classes_string}",
            ]

            if "sub_col" in locals() and sub_col is not None and sub_col != "--":
                plotting_args += ["--sub_col", f"{sub_col}"]

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

            (
                image_col_size,
                st.session_state["show_greyscale"],
            ) = DownloadHeader.slider_and_image_download(
                filepath=conf_mat_path,
                download_label="Download plot",
                slider_label="Zoom",
                toggle_label="Show greyscale",
                toggle_value=True,
                toggle_cols=[10, 1],
                slider_help="Zoom in/out to better match the size you expect to have in a paper etc. "
                "This affects the font sizes and will likely lead to adjustments of `height` and `width`.",
            )
            st.session_state["image_col_size"] = (
                min_max_scale_list(
                    x=[image_col_size],
                    new_min=2.0,
                    new_max=8.0,
                    old_min=0.0,
                    old_max=1.0,
                )[0]
                if image_col_size <= 1
                else min_max_scale_list(
                    x=[image_col_size],
                    new_min=8.0,
                    new_max=23.0,
                    old_min=1.0,
                    old_max=2.0,
                )[0]
            )

            col1, col2, col3 = st.columns([2, st.session_state["image_col_size"], 2])
            with col2:
                st.write(" ")
                st.write(" ")
                image = Image.open(str(conf_mat_path)[:-3] + "jpg")
                st.image(
                    image,
                    caption="Confusion Matrix",
                    clamp=False,
                    channels="RGB",
                    output_format="auto",
                )

                if st.session_state["show_greyscale"]:
                    # Convert the image to grayscale
                    st.write(" ")
                    image = image.convert("CMYK").convert("L")
                    st.image(
                        image,
                        caption="Greyscale version for assessing colors in print",
                        clamp=False,
                        channels="RGB",
                        output_format="auto",
                    )
                st.write(" ")
                st.write("Note: The downloadable file has a transparent background.")

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
