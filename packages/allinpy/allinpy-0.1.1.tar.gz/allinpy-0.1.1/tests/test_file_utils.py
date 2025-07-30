import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
import pandas as pd

from allinpy import get_df_subj, load_data, sorted_nicely


class TestUtilities(unittest.TestCase):

    def test_get_df_subj(self):
        """This function tests the function that selects the subject-specific data frames."""

        # Create input data frame
        df_subj = pd.DataFrame(index=np.arange(10) + 20)
        df_subj["subj_num"] = np.array([30, 30, 30, 30, 30, 31, 31, 31, 31, 31])
        df_subj["test"] = np.arange(10)

        # Extract subject-specific data frame
        df_subj = get_df_subj(df_subj, 30)

        # Create expected data frame
        expected_df = pd.DataFrame(index=np.arange(5))
        expected_df["subj_num"] = np.array(
            [31, 31, 31, 31, 31]
        )  # expected bc. Python starts counting at 0
        expected_df["test"] = np.arange(5) + 5

        # Test output
        df_subj.equals(expected_df)

    def test_sorted_nicely(self):
        """This function tests the sorting function used for sorting the file paths."""

        file_paths = [
            "al_data/first_experiment/sub_5/behav/sub-5_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_1/behav/sub-1_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_8/behav/sub-8_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_4/behav/sub-4_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_2/behav/sub-2_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_6/behav/sub-6_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_9/behav/sub-9_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_3/behav/sub-3_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_10/behav/sub-10_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_7/behav/sub-7_task-helicopter_behav.tsv",
        ]

        # Sort all file names according to participant ID
        file_paths_sorted = sorted_nicely(file_paths)

        # Expected test results
        file_paths_expected = [
            "al_data/first_experiment/sub_1/behav/sub-1_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_2/behav/sub-2_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_3/behav/sub-3_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_4/behav/sub-4_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_5/behav/sub-5_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_6/behav/sub-6_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_7/behav/sub-7_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_8/behav/sub-8_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_9/behav/sub-9_task-helicopter_behav.tsv",
            "al_data/first_experiment/sub_10/behav/sub-10_task-helicopter_behav.tsv",
        ]

        self.assertTrue(file_paths_sorted == file_paths_expected)

    def setUp(self):
        """Set up a temporary test environment before each test.

            Creates a temporary directory and generates test files
            containing 400 rows of simulated data. The file paths are
            stored in `self.f_names` for use in test cases.
        """

        self.temp_dir = tempfile.TemporaryDirectory()
        self.f_names = []

        # Create two full datasets with 400 rows
        for i in range(2):
            df = pd.DataFrame({
                "stimulus": np.random.rand(400),
                "response": np.random.rand(400),
            })
            file_path = Path(self.temp_dir.name) / f"sub-{i}_task.tsv"
            df.to_csv(file_path, sep="\t", index=False)
            self.f_names.append(file_path)

        # Add one short (incomplete) dataset
        self.short_file = Path(self.temp_dir.name) / "short.tsv"
        df_short = pd.DataFrame({"stimulus": np.random.rand(2)})
        df_short.to_csv(self.short_file, sep="\t", index=False)

    def tearDown(self):
        """
        Clean up after each test by deleting the temporary directory and files.
        """
        self.temp_dir.cleanup()

    def test_load_data_combines_correctly(self):
        """This function tests the function that loads the data frames."""

        df = load_data(self.f_names, expected_n_trials=400)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 800)
        self.assertIn("trial", df.columns)
        self.assertEqual(df["trial"].iloc[0], 0)
        self.assertEqual(df["trial"].iloc[399], 399)
        self.assertEqual(df["trial"].iloc[400], 0)

    def test_prints_warning_on_missing_trials(self):
        """ Tests if the function correctly returns the number of trials when unequal
            to expecte T trials.
        """
        with patch("builtins.print") as mock_print:
            load_data([self.short_file], expected_n_trials=400)

        # Access printed string via call arguments
        printed_args = mock_print.call_args[0]  # First call, first positional args
        printed_text = printed_args[0]  # The string passed to print()
        self.assertIn("2 trials", printed_text)