import pandas as pd
import pkg_resources

from utils.config import Config
from utils.constants import (
    DATASET_NOT_LOADED,
    SERVER_LIVE,
    IRIS_DATASET_PATH,
)
from utils.loggr import LOG

# Global Objects

# Currently only single static one, further improvement include multiple
# datasets (dict of datasets) possibly loaded (lazily?) from a database.
DATASET: pd.DataFrame = pd.read_csv(IRIS_DATASET_PATH)

CONFIG: Config = None

# General server state, can add fields if need be.
SERVER_STATE: dict = {
    "state": ["NA"],
    "message": ["NA"],
    "LIVE": False,
}


OPENDP_VERSION = pkg_resources.get_distribution("opendp").version


def check_start_condition():
    """
    This function checks the server started correctly and SERVER_STATE is
    updated accordingly.

    This has potential side effects on the return values of the "depends"
    functions, which check the server state.
    """
    global DATASET, CONFIG, SERVER_STATE
    if DATASET is None:
        LOG.info("Dataset not loaded")
        SERVER_STATE["state"].append(DATASET_NOT_LOADED)
        SERVER_STATE["message"].append("Server could not be started!")
        SERVER_STATE["LIVE"] = False
    else:
        LOG.info("Dataset successfully  loaded")
        SERVER_STATE["state"].append(SERVER_LIVE)
        SERVER_STATE["message"].append("Server started!")
        SERVER_STATE["LIVE"] = True
