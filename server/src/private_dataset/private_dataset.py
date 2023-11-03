from abc import ABC, abstractmethod
import pandas as pd
import shutil

<<<<<<< HEAD
from dataset_store.private_dataset_observer import PrivateDatasetObserver
=======
from constants import SSQL_METADATA_OPTIONS
>>>>>>> ad579f41410f68c8d2f6f4ba3569ac64a764eeb0


class PrivateDataset(ABC):
    """
    Overall access to sensitive data
    """

    df = None
    local_path = None
    local_dir = None

<<<<<<< HEAD
    def __init__(self, metadata: dict) -> None:
=======
    def __init__(self, metadata) -> None:
>>>>>>> ad579f41410f68c8d2f6f4ba3569ac64a764eeb0
        """
        Connects to the DB
        Parameters:
            - metadata: The metadata for this dataset
        """
        self.metadata = metadata
<<<<<<< HEAD
        self.dataset_observers = []
=======
        self.dtypes = get_dtypes(metadata)
>>>>>>> ad579f41410f68c8d2f6f4ba3569ac64a764eeb0

    def __del__(self):
        """
        Cleans up the temporary directory used for storing
        the dataset locally if needed.
        """
        if self.local_dir is not None:
            shutil.rmtree(self.local_dir)

    @abstractmethod
    def get_local_path(self) -> str:
        """
        Get the path to  a local copy of the file.
        Returns:
            - path
        """
        pass

    @abstractmethod
    def get_pandas_df(self, dataset_name: str) -> pd.DataFrame:
        """
        Get the data in pandas dataframe format
        Parameters:
            - dataset_name: name of the private dataset
        """
        pass

    def get_metadata(self) -> dict:
        """
        Get the metadata for this dataset
        """
        return self.metadata

<<<<<<< HEAD
    def get_memory_usage(self) -> int:
        """
        Returns the memory usage of this dataset, in MiB.

        The number returned only takes into account the memory usage
        of the pandas DataFrame "cached" in the instance.
        """
        if self.df is None:
            return 0
        else:
            return self.df.memory_usage().sum() / (1024**2)

    def subscribe_for_memory_usage_updates(
        self, dataset_observer: PrivateDatasetObserver
    ):
        """
        Add the PrivateDatasetObserver to the list of dataset_observers.
        """
        self.dataset_observers.append(dataset_observer)
=======

def get_dtypes(metadata: str) -> dict:
    dtypes = {}
    for col_name, data in metadata[""]["Schema"]["Table"].items():
        if col_name in SSQL_METADATA_OPTIONS:
            continue
        dtypes[col_name] = data["type"]
    return dtypes
>>>>>>> ad579f41410f68c8d2f6f4ba3569ac64a764eeb0
