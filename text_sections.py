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
        st.write(
            "This application allows you to plot a confusion matrix based on your own data. "
        )
    with col2:
        st.image(
            "https://github.com/LudvigOlsen/cvms/raw/master/man/figures/cvms_logo_242x280_250dpi.png",
            width=125,
        )

    st.write(
        "The plot is created with the [**cvms**](https://github.com/LudvigOlsen/cvms) R package "
        f"(v/{get_cvms_version()}, LR Olsen & HB Zachariae, 2019)."
    )

    st.write(
        "DATA PRIVACY: In order to transfer the data "
        "between python and R, it is temporarily stored on the servers. "
        "While we, the authors, have no intention of looking at your data, we make "
        "*no guarantees* about the privacy of your data (it is not our servers). "
        "Please do not upload sensitive data. The application "
        "only requires columns with predictions and targets."
    )


def generate_data_text():
    st.subheader("Generate data")
    st.write(
        "If you just want to try out the application, you can generate a dataset with targets and predictions. "
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
