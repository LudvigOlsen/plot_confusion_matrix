import json
import pathlib
import pandas as pd
import streamlit as st
from utils import call_subprocess

from components import add_toggle_vertical


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
    def slider_and_image_download(
        filepath,
        slider_label,
        toggle_label,
        download_label="Download",
        slider_min=0.0,
        slider_max=2.0,
        slider_value=1.0,
        slider_step=0.1,
        slider_help=None,
        toggle_value=False,
        toggle_cols=[2, 5],
        download_help="Download plot",
        key=None,
    ) -> int:
        col1, col2, col3, col4 = st.columns([2, 6, 3, 3])
        with col2:
            # Image viewing size slider
            image_col_size = st.slider(
                slider_label,
                min_value=slider_min,
                max_value=slider_max,
                value=slider_value,
                step=slider_step,
                help=slider_help,
                key=key + "_slider" if key is not None else key,
            )
        with col3:
            toggle_state = add_toggle_vertical(
                label=toggle_label,
                key=key + "_toggle" if key is not None else key,
                default=toggle_value,
                cols=toggle_cols,
            )
        with col4:
            st.write("")
            with open(filepath, "rb") as img:
                st.download_button(
                    label=download_label,
                    data=img,
                    file_name=pathlib.Path(filepath).name,
                    mime="image/png",
                    key=key + "_download" if key is not None else key,
                    help=download_help,
                )
        return image_col_size, toggle_state

    @staticmethod
    def _convert_df_to_csv(data, **kwargs):
        return data.to_csv(**kwargs).encode("utf-8")

    @staticmethod
    def header_and_data_download(
        header,
        data,
        file_name,
        col_sizes=[9, 2],
        key=None,
        label="Download",
        help="Download data",
    ):
        col1, col2 = st.columns(col_sizes)
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

    @staticmethod
    def centered_json_download(
        data: dict,
        file_name,
        download_col_size=5,
        key=None,
        label="Download",
        help="Download json file",
    ):
        col1, col2, col1 = st.columns([5, download_col_size, 5])
        with col2:
            data_json = json.dumps(data)
            st.download_button(
                label=label,
                data=data_json,
                file_name=file_name,
                key=key,
                mime="application/json",
                help=help,
            )
