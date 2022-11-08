from opendp.mod import enable_features
enable_features('contrib', 'floating-point')
from fastapi import HTTPException

import globals


def opendp_apply(client_measurement):
    # attempt to compute the privacy utilization of the measurement, an individual may influence one row
    try:
        usage = client_measurement.map(d_in=1)
    except Exception as ex:
        globals.LOG.exception(ex)
        raise HTTPException(400, 'Error evaluating privacy map for the chain. Error:' + str(e))
    
    # unpack the privacy usage
    try: 
        e, d = usage
    except:
        raise HTTPException(400, "Please ensure the privacy map returns an (ε, δ) tuple: https://docs.opendp.org/en/stable/user/constructors/combinators.html#measure-casting")
    
    if e > globals.EPSILON_LIMIT:
        raise HTTPException(400, f"Chain constructed uses epsilon > {globals.EPSILON_LIMIT}, please update and retry")
    if d > globals.DELTA_LIMIT:
        raise HTTPException(400, f"Chain constructed uses delta > {globals.DELTA_LIMIT}, please update and retry")

    # invoke the measurement
    try:
        release_data = client_measurement(globals.TRAIN.to_csv(header=False, index=False))
    except Exception as e:
        globals.LOG.exception(e)
        raise HTTPException(400, "Failed when applying chain to data with error: " + str(e))
    
    return release_data, (e, d)