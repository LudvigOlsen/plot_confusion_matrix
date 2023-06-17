import subprocess
import re
import streamlit as st
import json
from typing import Optional


def show_error(msg, action):
    st.error(
        f"Failed to {action}:\n\n...{msg}\n\nPlease [report](https://github.com/LudvigOlsen/plot_confusion_matrix/issues) this issue."
    )


def call_subprocess(call_, message, return_output=False, encoding="UTF-8"):
    # With capturing of output
    if return_output:
        try:
            out = subprocess.check_output(call_, shell=True, encoding=encoding)
        except subprocess.CalledProcessError as e:
            if "Failed to create plot from confusion matrix." in e.output:
                msg = e.output.split("Failed to create plot from confusion matrix.")[-1]
                show_error(msg=msg, action="plot confusion matrix")
            elif "Failed to read design settings as a json file" in e.output:
                msg = e.output.split("Failed to read design settings as a json file")[
                    -1
                ]
                show_error(msg=msg, action="read design settings")
            elif "Failed to read data from" in e.output:
                msg = e.output.split("Failed to read data from")[-1]
                show_error(msg=msg, action="read data")
            elif "Failed to ggsave plot to:" in e.output:
                msg = e.output.split("Failed to ggsave plot to:")[-1]
                show_error(msg=msg, action="save plot")
            else:
                msg = e.output.split("\n\n")[-1]
                st.error(
                    f"Unknown type of error: {msg}.\n\n"
                    "Please [report](https://github.com/LudvigOlsen/plot_confusion_matrix/issues) this issue."
                )
            print(e.output)
            print(f"{message}: {call_}")
            raise e
        return out

    # Without capturing of output
    try:
        subprocess.check_call(call_, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"{message}: {call_}")
        raise e


def clean_string_for_non_alphanumerics(s):
    # Remove non-alphanumerics (keep spaces)
    pattern1 = re.compile("[^0-9a-zA-Z\s]+")
    # Replace multiple spaces with a single space
    pattern2 = re.compile("\s+")
    # Apply replacements
    s = pattern1.sub("", s)
    s = pattern2.sub(" ", s)
    # Trim whitespace in start and end
    return s.strip()


def clean_str_column(x):
    return x.astype(str).apply(lambda x: clean_string_for_non_alphanumerics(x))


def min_max_scale_list(
    x: list,
    new_min: float,
    new_max: float,
    old_min: Optional[float] = None,
    old_max: Optional[float] = None,
) -> list:
    """
    MinMax scaler for lists.
    Why: Currently we don't require numpy as dependency.
    """
    if old_min is None:
        old_min = min(x)
    if old_max is None:
        old_max = max(x)

    diff = old_max - old_min

    # Avoiding zero-division
    if diff == 0:
        diff = 1

    x = [(xi - old_min) / diff for xi in x]
    return [xi * (new_max - new_min) + new_min for xi in x]
