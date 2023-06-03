import subprocess
import re


def call_subprocess(call_, message, return_output=False, encoding="UTF-8"):
    # With capturing of output
    if return_output:
        try:
            out = subprocess.check_output(call_, shell=True, encoding=encoding)
        except subprocess.CalledProcessError as e:
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
    pattern = re.compile("[\W'_']+")
    return pattern.sub("", s)
