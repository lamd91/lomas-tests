from abc import ABC, abstractmethod
from fastapi import Header, HTTPException
from typing import Dict

from utils.constants import (
    SUPPORTED_LIBS,
    LIB_SMARTNOISE_SQL,
    DATASET_PATHS,
    DATASET_METADATA_PATHS,
)
from database.database import Database
from dp_queries.input_models import BasicModel
from utils.loggr import LOG


class DPQuerier(ABC):
    """
    Overall query to external DP library
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Initialise with specific dataset
        """
        pass

    @abstractmethod
    def cost(self, query_str: str, eps: float, delta: float) -> [float, float]:
        """
        Estimate cost of query
        """
        pass

    @abstractmethod
    def query(self, query_str: str, eps: float, delta: float) -> list:
        """
        Does the query and return the response
        """
        pass


class QuerierManager(ABC):
    """
    Manages the DPQueriers for the different datasets and libraries

    Holds a reference to the database in order to get information about
    the datasets.

    We make the _add_dataset function private to enforce lazy loading of
    queriers.
    """

    database: Database

    def __init__(self, database: Database) -> None:
        self.database = database

    @abstractmethod
    def _add_dataset(self, dataset_name: str) -> None:
        """
        Adds a dataset to the manager
        """
        pass

    @abstractmethod
    def get_querier(self, dataset_name: str, library: str) -> DPQuerier:
        """
        Returns the querier for the given dataset and library
        """
        pass


class BasicQuerierManager(QuerierManager):
    """
    Basic implementation of the QuerierManager interface.

    The queriers are initialized lazily and put into a dict.
    There is no memory management => The manager will fail if the datasets are
    too large to fit in memory.

    The _add_dataset method just gets the source data from csv files
    (links stored in constants).
    """

    dp_queriers: Dict[str, Dict[str, DPQuerier]] = None

    def __init__(self, database: Database) -> None:
        super().__init__(database)
        self.dp_queriers = {}
        return

    def _add_dataset(self, dataset_name: str) -> None:
        """
        Adds all queriers for a dataset.
        The source data is fetched from an online csv, the paths are stored
        as constants for now.

        TODO Get the info from the metadata stored in the db.
        """
        # Should not call this function if dataset already present.
        assert (
            dataset_name not in self.dp_queriers
        ), "BasicQuerierManager: Trying to add a dataset already in self.dp_queriers"

        # Initialize dict
        self.dp_queriers[dataset_name] = {}

        for lib in SUPPORTED_LIBS:
            if lib == LIB_SMARTNOISE_SQL:
                ds_path = DATASET_PATHS[dataset_name]
                ds_metadata_path = DATASET_METADATA_PATHS[dataset_name]
                from dp_queries.smartnoise_json.smartnoise_sql import (
                    SmartnoiseSQLQuerier,
                )

                querier = SmartnoiseSQLQuerier(ds_path, ds_metadata_path)

                self.dp_queriers[dataset_name][lib] = querier
            # elif ... :
            else:
                raise Exception(
                    f"Trying to create a querier for library {lib}. "
                    "This should never happen."
                )

    def get_querier(self, dataset_name: str, library: str) -> DPQuerier:
        if dataset_name not in self.dp_queriers:
            self._add_dataset(dataset_name)

        return self.dp_queriers[dataset_name][library]


class QueryHandler:
    """
    Query handler for the server.

    Holds a reference to the database and uses a BasicQuerierManager
    to manage the queriers. TODO make this configurable?
    """

    database: Database
    querier_manager: BasicQuerierManager

    def __init__(self, database: Database) -> None:
        self.database = database
        self.querier_manager = BasicQuerierManager(database)
        return

    def handle_query(
        self,
        query_type: str,
        query_json: BasicModel,
        x_oblv_user_name: str = Header(None),
    ):
        # Check query type
        if query_type not in SUPPORTED_LIBS:
            e = f"Query type {query_type} not supported in QueryHandler"
            LOG.exception(e)
            raise HTTPException(404, str(e))

        # Get querier
        try:
            dp_querier = self.querier_manager.get_querier(
                query_json.dataset_name, query_type
            )
        except Exception as e:
            LOG.exception(
                f"Failed to get querier for dataset"
                f"{query_json.dataset_name}: {str(e)}"
            )
            raise HTTPException(
                404,
                f"Failed to get querier for dataset"
                f"{query_json.dataset_name}",
            )

        # Get cost of the query
        eps_cost, delta_cost = dp_querier.cost(
            query_json.query_str, query_json.epsilon, query_json.delta
        )

        # Check that enough budget to to the query
        eps_max_user, delta_max_user = self.database.get_max_budget(
            x_oblv_user_name, query_json.dataset_name
        )
        eps_curr_user, delta_curr_user = self.database.get_current_budget(
            x_oblv_user_name, query_json.dataset_name
        )

        # If enough budget
        if ((eps_max_user - eps_curr_user) >= eps_cost) and (
            (delta_max_user - delta_curr_user) >= delta_cost
        ):
            # Query
            try:
                response, _ = dp_querier.query(
                    query_json.query_str, query_json.epsilon, query_json.delta
                )
            except HTTPException as he:
                LOG.exception(he)
                raise he
            except Exception as e:
                LOG.exception(e)
                raise HTTPException(500, str(e))

            # Deduce budget from user
            self.database.update_budget(
                x_oblv_user_name, query_json.dataset_name, eps_cost, delta_cost
            )

            # Add query to db (for archive)
            self.database.save_query(
                x_oblv_user_name,
                query_json.dataset_name,
                eps_cost,
                delta_cost,
                query_json.query_str,
            )

        # If not enough budget, do not update nor return response
        else:
            response = {
                "requested_by": x_oblv_user_name,
                "state": f"Not enough budget to perform query. \
                Nothing was done. \
                Current epsilon: {eps_curr_user}, \
                Current delta {delta_curr_user} \
                Max epsilon: {eps_max_user}, Max delta {delta_max_user} ",
            }

        # Return response
        return response