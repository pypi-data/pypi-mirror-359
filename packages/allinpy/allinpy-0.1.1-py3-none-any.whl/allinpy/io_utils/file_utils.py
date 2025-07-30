import os
import re
from fnmatch import fnmatch
from pathlib import Path

import numpy as np
import pandas as pd


def get_df_subj(df: pd.DataFrame, i: int) -> pd.DataFrame:
    """This function creates a subject-specific data frame with adjusted index.

    Parameters
    ----------
    df : pd.DataFrame
        Subject data frame.
    i : int
        Subject number.

    Returns
    -------
    pd.DataFrame
        Index-adjusted subject-specific data frame (df_subj).
    """

    df_subj = df[(df["subj_num"] == i + 1)].copy()
    df_subj = df_subj.reset_index(drop=True)  # adjust index

    return df_subj


def load_data(f_names: list[Path], expected_n_trials: int = 400) -> pd.DataFrame:
    """This function loads the adaptive learning BIDS data and checks if they are complete.

    Parameters
    ----------
    f_names : list[Path]
        List with all file names.
    expected_n_trials : int
        Expected number of trials.

    Returns
    -------
    pd:DataFrame
        Data frame that contains all data.
    """

    all_dfs = []
    n_trials = []

    for i, fname in enumerate(f_names):
        df = pd.read_csv(fname, sep="\t", header=0)

        n = len(df)
        n_trials.append(n)

        if n_trials[-1] != expected_n_trials:
            print(f"{fname}: {n} trials")

        df["trial"] = np.arange(n, dtype=np.int64)
        all_dfs.append(df)

    all_data = pd.concat(all_dfs, ignore_index=True)

    return all_data


def sorted_nicely(input_list: list) -> list:
    """This function sorts the given iterable in the way that is expected.

    Obtained from:
    https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python

    Parameters
    ----------
    input_list : list
        The iterable to be sorted.

    Returns
    -------
    list
        Sorted iterable.
    """

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(input_list, key=alphanum_key)


def get_file_paths(folder_path: Path, identifier: str) -> list[str]:
    """This function extracts the file path.

    Parameters
    ----------
    folder_path : Path
        Relative path to current folder.
    identifier : Path
        Identifier for file of interest.

    Returns
    -------
    list[str]
        Absolute path to file (file_paths).
    """

    file_paths = []
    for path, subdirs, files in os.walk(folder_path):

        for name in files:
            if fnmatch(name, identifier):
                file_paths.append(os.path.join(path, name))

    return file_paths
