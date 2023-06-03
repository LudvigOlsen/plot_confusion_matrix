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
