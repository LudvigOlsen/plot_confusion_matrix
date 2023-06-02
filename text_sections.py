import streamlit as st
from utils import call_subprocess


@st.cache_resource
def get_cvms_version():
    return (
        str(
            call_subprocess(
                f"Rscript cvms_version.R",
                message="cvms versioning script",
                return_output=True,
                encoding="UTF-8",
            )
        )
        .split("[1]")[-1]
        .replace("‘", "")
        .replace("’", "")
    )


def intro_text():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("Plot Confusion Matrix")
        st.markdown(
            "A confusion matrix plot is a great tool for inspecting your "
            "machine learning model's performance on a classification task. "
            "This application enables you to plot a confusion matrix on your own data, "
            "**without a single line of code**. \n\n"
            "It's designed for high flexibility AND quick results with good default settings.\n\n"
        )
    with col2:
        st.image(
            "https://github.com/LudvigOlsen/cvms/raw/master/man/figures/cvms_logo_242x280_250dpi.png",
            width=125,
        )
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Have your data ready?")
        st.markdown(  # TODO: Make A,B, etc. icons
            "Upload a csv file with either: \n\n"
            "A) **Targets** and **predictions**. \n\n"
            "B) Existing confusion matrix **counts**. \n\n"
            "--> Specify the columns to use.\n\n"
            "--> Press **Generate plot**.\n\n"
        )
    with col2:
        st.subheader("No data to upload?")
        st.markdown(
            "No worries! Either: \n\n"
            "C) **Input** your counts directly! \n\n"
            "D) **Generate** some data with **very** easy controls! \n\n"
            "--> Press **Generate plot**.\n\n"
        )
    st.markdown("""---""")
    st.markdown(
        "This release is a **beta** version. Report errors or suggestions "
        "on [GitHub](https://github.com/LudvigOlsen/cvms_plot_app/issues)."
    )
    st.write(
        "The plot is created with the [**cvms**](https://github.com/LudvigOlsen/cvms) R package "
        f"(v/{get_cvms_version()}, LR Olsen & HB Zachariae, 2019)."
    )  # TODO Add citation stuff

    st.markdown(
        '<p class="small-font">'
        "DATA PRIVACY: For technical reasons, the uploaded data is temporarily stored "
        "on the server. While we, the authors, won't access your data, we make "
        "*no guarantees* about the privacy of your data (not our servers). "
        "Please do not upload sensitive data. The application "
        "only requires either predictions and targets or counts. "
        "</p>",
        unsafe_allow_html=True,
    )


def generate_data_text():
    st.subheader("Generate data")
    st.write(
        "Quickly try the application by generating a dataset with targets and predictions. "
        "Select a number of classes and observations, and you're ready to go! "
    )


def enter_count_data_text():
    st.subheader("Enter counts")
    st.write(
        "If you already have the confusion matrix counts and want to plot them. "
        "Enter the counts and get designing! "
    )
    st.write("Start by entering the names of your classes:")


def upload_counts_text():
    st.subheader("Upload your counts")
    st.write(
        "Plot an existing confusion matrix (counts of target-prediction combinations). "
        "The application expects a `.csv` file with: \n"
        "1) A `target classes` column. \n\n"
        "2) A `predicted classes` column. \n\n"
        "3) A `combination count` column for the "
        "combination frequency of 1 and 2. \n\n"
        "Other columns are currently ignored. "
        "See example of such a .csv file [here] (TODO). "
    )


def upload_predictions_text():
    st.subheader("Upload your predictions")
    st.markdown(
        "The application expects a `.csv` file with:  \n"
        "1) A `target` column.  \n"
        "Targets will be converted into strings. \n\n"
        "2) A `prediction` column.  \n"
        "Predictions can be probabilities (binary classification only) or class predictions. \n\n"
        "Other columns are currently ignored.  \n\n"
        "You will have the option to select the names of these two columns, so don't "
        "worry too much about the column names in the uploaded data."
    )


def columns_text():
    st.subheader("Specify columns")
    st.write(
        "Please select which of the columns in the data should be used for targets and predictions."
    )


def design_text():
    st.subheader("Design your plot")
    st.write("This is where you customize the design of your confusion matrix plot.")
    st.markdown(
        "The *width* and *height* settings are usually necessary to adjust as they "
        "change the relative size of the elements. Try adjusting 100px at a "
        "time for a start."
    )
    st.write(
        "If you have previously saved your preferred design settings, "
        "you can start by uploading the json file. "
        "Otherwise, get designing!"
    )
