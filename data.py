import pathlib
import pandas as pd
import streamlit as st
from utils import call_subprocess


def read_data(data):
    if data is not None:
        df = pd.read_csv(data)
        return df
    else:
        return None


@st.cache_data
def read_data_cached(data):
    return read_data(data)


def generate_data(out_path, num_classes, num_observations, seed) -> None:
    call_subprocess(
        f"Rscript generate_data.R --out_path {out_path} --num_classes {num_classes} --num_observations {num_observations} --seed {seed}",
        message="Data generation script",
        return_output=True,
        encoding="UTF-8",
    )


class DownloadHeader:
    """
    Class for showing header and download button (for an image file) in the same row.
    """

    @staticmethod
    def header_and_image_download(
        header, filepath, key=None, label="Download", help="Download plot"
    ):
        col1, col2 = st.columns([9, 2])
        with col1:
            st.subheader(header)
        with col2:
            st.write("")
            with open(filepath, "rb") as img:
                st.download_button(
                    label=label,
                    data=img,
                    file_name=pathlib.Path(filepath).name,
                    mime="image/png",
                    key=key,
                    help=help,
                )

    @staticmethod
    def _convert_df_to_csv(data, **kwargs):
        return data.to_csv(**kwargs).encode("utf-8")

    @staticmethod
    def header_and_data_download(
        header, data, file_name, key=None, label="Download", help="Download data"
    ):
        col1, col2 = st.columns([9, 2])
        with col1:
            st.subheader(header)
        with col2:
            st.write("")
            st.download_button(
                label=label,
                data=DownloadHeader._convert_df_to_csv(data, index=False),
                file_name=file_name,
                key=key,
                help=help,
            )
