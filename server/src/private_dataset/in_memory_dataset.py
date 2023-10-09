import os
import pandas as pd
import shutil
import tempfile

from private_dataset.private_dataset import PrivateDataset


class InMemoryDataset(PrivateDataset):
    """
    Class to hold a dataset created from an in-memory pandas DataFrame
    """

    def __init__(self, metadata, dataset_df) -> None:
        """
        Parameters:
            - dataset_df: Dataframe of the dataset
        """
        super().__init__(metadata)
        self.df = dataset_df.copy()
        self.local_path = None
        self.local_dir = None

    def __del__(self):
        """
        Cleans up the temporary directory used for storing
        the dataset locally if needed.
        """
        if self.local_dir is not None:
            shutil.rmtree(self.local_dir)

    def get_pandas_df(self) -> pd.DataFrame:
        """
        Get the data in pandas dataframe format
        Returns:
            - pandas dataframe of dataset (a copy)
        """
        # We use a copy here for safety.
        return self.df.copy()

    def get_local_path(self) -> str:
        """
        Get the path to a local copy of the source data in csv format.
        Returns:
            - path
        """

        if self.local_path is None:
            # Create temp dir and file
            self.local_dir = tempfile.mkdtemp()
            file_name = self.ds_path.split("/")[-1]
            self.local_path = os.path.join(self.local_dir, file_name)

            self.df.to_csv(self.local_path)

        return self.local_path
