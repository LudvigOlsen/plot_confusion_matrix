import streamlit as st
import pandas as pd
from utils import call_subprocess


def insert_arrow():
    return '<svg xmlns="http://www.w3.org/2000/svg" style="width:25px;" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H3" /></svg>'


def insert_chart_icon(choice=0):
    if choice == 0:
        return '<svg xmlns="http://www.w3.org/2000/svg" style="width:25px;" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M3 3.5A1.5 1.5 0 014.5 2h6.879a1.5 1.5 0 011.06.44l4.122 4.12A1.5 1.5 0 0117 7.622V16.5a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 013 16.5v-13zM13.25 9a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5a.75.75 0 01.75-.75zm-6.5 4a.75.75 0 01.75.75v.5a.75.75 0 01-1.5 0v-.5a.75.75 0 01.75-.75zm4-1.25a.75.75 0 00-1.5 0v2.5a.75.75 0 001.5 0v-2.5z" clip-rule="evenodd" /></svg>'
    else:
        return '<svg xmlns="http://www.w3.org/2000/svg" style="width:25px;" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M4.5 2A1.5 1.5 0 003 3.5v13A1.5 1.5 0 004.5 18h11a1.5 1.5 0 001.5-1.5V7.621a1.5 1.5 0 00-.44-1.06l-4.12-4.122A1.5 1.5 0 0011.378 2H4.5zm2.25 8.5a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5zm0 3a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5z" clip-rule="evenodd" /></svg>'


def insert_edit_icon():
    return '<svg xmlns="http://www.w3.org/2000/svg" style="width:25px;" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" /><path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" /></svg>'


def insert_generate_icon():
    return '<svg xmlns="http://www.w3.org/2000/svg" style="width:25px;" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M10 1a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 1zM5.05 3.05a.75.75 0 011.06 0l1.062 1.06A.75.75 0 116.11 5.173L5.05 4.11a.75.75 0 010-1.06zm9.9 0a.75.75 0 010 1.06l-1.06 1.062a.75.75 0 01-1.062-1.061l1.061-1.06a.75.75 0 011.06 0zM3 8a.75.75 0 01.75-.75h1.5a.75.75 0 010 1.5h-1.5A.75.75 0 013 8zm11 0a.75.75 0 01.75-.75h1.5a.75.75 0 010 1.5h-1.5A.75.75 0 0114 8zm-6.828 2.828a.75.75 0 010 1.061L6.11 12.95a.75.75 0 01-1.06-1.06l1.06-1.06a.75.75 0 011.06 0zm3.594-3.317a.75.75 0 00-1.37.364l-.492 6.861a.75.75 0 001.204.65l1.043-.799.985 3.678a.75.75 0 001.45-.388l-.978-3.646 1.292.204a.75.75 0 00.74-1.16l-3.874-5.764z" clip-rule="evenodd" /></svg>'


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


@st.cache_data
def get_example_counts():
    return pd.DataFrame(
        {
            "Target": ["cl1", "cl2", "cl1", "cl2"],
            "Prediction": ["cl1", "cl2", "cl2", "cl1"],
            "Sub*": [
                "(57/60)",
                "(46/50)",
                "(12/15)",
                "(23/25)",
            ],
            "N": [12, 10, 3, 5],
        }
    )


@st.cache_data
def get_example_data():
    return pd.DataFrame(
        {
            "Target": ["cl1", "cl1", "cl2", "cl2", "cl1", "cl1"],
            "Prediction": ["cl1", "cl2", "cl2", "cl1", "cl1", "cl2"],
        }
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
            "It's designed for high flexibility AND quick results with "
            "templates and good default settings.\n\n"
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
            f"{insert_chart_icon(1)} **Targets** and **predictions** \n\n"
            f"{insert_chart_icon(0)} Existing confusion matrix **counts** \n\n"
            f"{insert_arrow()} Specify the columns to use\n\n"
            f"{insert_arrow()} Press **Generate plot**\n\n",
            unsafe_allow_html=True,
        )
    with col2:
        st.subheader("No data to upload?")
        st.markdown(
            "No worries! Either: \n\n"
            f"{insert_edit_icon()} **Input** your counts directly! \n\n"
            f"{insert_generate_icon()} **Generate** some data with **very** easy controls! \n\n"
            f"{insert_arrow()} Press **Generate plot**\n\n",
            unsafe_allow_html=True,
        )
    st.markdown("""---""")
    st.markdown(
        "This release is an **alpha** version (very early). Report errors or suggestions "
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
    )
    col1, col2 = st.columns([5, 4])
    with col1:
        st.markdown(
            "The application expects a `.csv` file with: \n"
            "1) A `target classes` column. \n\n"
            "2) A `predicted classes` column. \n\n"
            "3) A `combination count` column for the "
            "combination frequency of 1 and 2. \n\n"
            "4) (\\***Optionally**) a `sub` column with text "
            "that replaces the bottom text in the middle of tiles. \n\n"
            "Other columns are currently ignored. "
            "In the next step, you will be asked to select the names of these two columns. "
        )
    with col2:
        st.write("Example of such a file:")
        st.dataframe(get_example_counts(), hide_index=True)


def upload_predictions_text():
    st.subheader("Upload your predictions")
    col1, col2 = st.columns([5, 4])
    with col1:
        st.markdown(
            "The application expects a `.csv` file with:  \n"
            "1) A `target` column.  \n"
            "2) A `prediction` column.  \n"
            "Predictions should be class predictions (not probabilities). \n\n"
            "Other columns are currently ignored.  \n\n"
            "In the next step, you will be asked to select the names of these two columns. "
        )
    with col2:
        st.write("Example of such a file:")
        st.dataframe(get_example_data(), hide_index=True)


def columns_text():
    st.subheader("Specify columns")
    st.write(
        "Please select which of the columns in the data should be used for targets and predictions."
    )


def design_text():
    st.subheader("Design your plot")
    st.write("This is where you customize the design of your confusion matrix plot.")
    st.markdown(
        "We suggest you go directly to `Generate plot` to see the starting point. Then go back and tweak to your liking! "
        "You can also select one of the templates or upload previously saved design settings."
    )
    st.markdown(
        "The *width* and *height* settings are usually necessary to adjust as they "
        "change the relative size of the elements. Try adjusting 100px at a "
        "time for a start."
    )
    st.write("Get designing!")
    st.write("")
