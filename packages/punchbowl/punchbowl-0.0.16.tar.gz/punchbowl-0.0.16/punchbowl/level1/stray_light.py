import os
import pathlib
import warnings

import numpy as np
from astropy.time import Time
from ndcube import NDCube

from punchbowl.data import load_ndcube_from_fits
from punchbowl.exceptions import (
    IncorrectPolarizationStateWarning,
    IncorrectTelescopeWarning,
    InvalidDataError,
    LargeTimeDeltaWarning,
)
from punchbowl.prefect import punch_task
from punchbowl.util import nan_percentile


def estimate_stray_light(
        filepaths: [str], percentile: float = 3, do_uncertainty: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Estimate the fixed stray light pattern using a percentile."""
    cubes = [load_ndcube_from_fits(path) for path in filepaths]

    data = np.array([cube.data for cube in cubes])
    stray_light_estimate = nan_percentile(data, percentile).squeeze()

    if not do_uncertainty:
        return stray_light_estimate

    uncertainty_squared = np.array([cube.uncertainty.array**2 for cube in cubes])
    uncertainty = np.sqrt(np.sum(uncertainty_squared, axis=0)) / len(filepaths)

    return stray_light_estimate, uncertainty


@punch_task
def remove_stray_light_task(data_object: NDCube, stray_light_path: pathlib.Path | str) -> NDCube:
    """
    Prefect task to remove stray light from an image.

    Stray light is light in an optical system which was not intended in the
    design.

    The PUNCH instrument stray light will be mapped periodically as part of the
    ongoing in-flight calibration effort. The stray light maps will be
    generated directly from the L0 and L1 science data. Separating instrumental
    stray light from the F-corona. This has been demonstrated with SOHO/LASCO
    and with STEREO/COR2 observations. It requires an instrumental roll to hold
    the stray light pattern fixed while the F-corona rotates in the field of
    view. PUNCH orbital rolls will be used to create similar effects.

    Uncertainty across the image plane is calculated using a known stray light
    model and the difference between the calculated stray light and the ground
    truth. The uncertainty is convolved with the input uncertainty layer to
    produce the output uncertainty layer.


    Parameters
    ----------
    data_object : NDCube
        data to operate on

    stray_light_path: pathlib
        path to stray light model to apply to data

    Returns
    -------
    NDCube
        modified version of the input with the stray light removed

    """
    if stray_light_path is None:
        data_object.meta.history.add_now("LEVEL1-remove_stray_light", "Stray light correction skipped")
        return data_object

    stray_light_path = pathlib.Path(stray_light_path)
    if not stray_light_path.exists():
        msg = f"File {stray_light_path} does not exist."
        raise InvalidDataError(msg)
    stray_light_model = load_ndcube_from_fits(stray_light_path)

    stray_light_model_date = Time(stray_light_model.meta["DATE-OBS"].value)
    observation_date = Time(data_object.meta["DATE-OBS"].value)
    if abs((stray_light_model_date - observation_date).to("day").value) > 14:
        msg=f"Calibration file {stray_light_path} contains data created greater than 2 weeks from the obsveration"
        warnings.warn(msg,LargeTimeDeltaWarning)

    if stray_light_model.meta["TELESCOP"].value != data_object.meta["TELESCOP"].value:
        msg=f"Incorrect TELESCOP value within {stray_light_path}"
        warnings.warn(msg, IncorrectTelescopeWarning)
    elif stray_light_model.meta["OBSLAYR1"].value != data_object.meta["OBSLAYR1"].value:
        msg=f"Incorrect polarization state within {stray_light_path}"
        warnings.warn(msg, IncorrectPolarizationStateWarning)
    elif stray_light_model.data.shape != data_object.data.shape:
        msg = f"Incorrect stray light function shape within {stray_light_path}"
        raise InvalidDataError(msg)
    else:
        data_object.data[:, :] -= stray_light_model.data[:, :]
        uncertainty = 0
        # TODO: when we have real uncertainties, use them
        # uncertainty = stray_light_model.uncertainty.array # noqa: ERA001
        data_object.uncertainty.array[...] = np.sqrt(data_object.uncertainty.array**2 + uncertainty**2)
        data_object.meta.history.add_now("LEVEL1-remove_stray_light",
                                         f"stray light removed with {os.path.basename(str(stray_light_path))}")
    return data_object
