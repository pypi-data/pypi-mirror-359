""" Module for retrieving ECMWF data and loading it into Xarray. """

# Standard libary
import xarray as xr

# Third-party
import earthkit.data as ekd
from ecmwfapi import ECMWFService

# Local
from preflexpart.utils import setup_logger
from preflexpart.input_fields import ML_FIELDS, SURFACE_FIELDS, CONSTANT_FIELDS, ETADOT_FIELDS

logger = setup_logger(__name__)

def load(temp_files: list[str]) -> dict[str, xr.DataArray]:
    """
    Load data from downloaded files into an xarray dictionary,
    including hybrid level coefficients ak and bk.

    Args:
        temp_files (List[str]): List of file paths to be loaded.

    Returns:
        Dict[str, xr.DataArray]: A dictionary where keys are variable names
         and values are DataArrays.
    """
    request = {
        "param": (
            list(ML_FIELDS.keys()) +
            list(ETADOT_FIELDS.keys()) +
            list(CONSTANT_FIELDS.keys()) +
            list(SURFACE_FIELDS.keys())
        )
    }

    try:
        ds_fl = ekd.from_source("file", temp_files)

        ds_list = ds_fl.to_xarray(profile="grib", split_dims="param", add_earthkit_attrs=True)

        data_dict = {
            list(ds.data_vars.keys())[0]: ds[list(ds.data_vars.keys())[0]]
            for ds in ds_list
            if ds.data_vars and list(ds.data_vars.keys())[0] in request["param"]
        }

        # Extract hybrid coeff ("pv") from GRIB message
        pv = data_dict["u"].earthkit.metadata.get("pv")

        if pv is not None:
            i = len(pv) // 2
            data_dict["ak"] = xr.DataArray(pv[:i], dims="level")
            data_dict["bk"] = xr.DataArray(pv[i:], dims="level")

        return data_dict

    except Exception as e:
        logger.error("Error loading files: {%s}", e)
        return {}

def download_ecmwf_data(
    startdate: str,
    enddate: str,
    starttime: str,
    max_level: int,
    input_dir: str,
):
    """
    Download the required IFS forecasts from MARS.

    Args:
        startdate (str): Start date in YYYY-MM-DD format.
        enddate (str): End date in YYYY-MM-DD format.
        max_level (int): Maximum vertical level number.
        data_source (str): Data source.
        input_dir (str): Input directory.

    Returns:
        None
    """
    server = ECMWFService("mars")
    ml_param_ids = list(ML_FIELDS.values())
    etadot_ids = list(ETADOT_FIELDS.values())
    surface_param_ids = list(SURFACE_FIELDS.values())
    constant_param_ids = list(CONSTANT_FIELDS.values())

    server.execute({
        'type': 'fc',
        'class': 'od',
        'stream': 'oper',
        'expver': '1',
        'date': f"{startdate}/to/{enddate}",
        'time': f"{starttime}",
        'levtype': 'ml',
        'levelist': f"40/to/{max_level}",
        'step': '0/to/90/by/1',
        'param': "/".join(ml_param_ids),
        'grid': '0.25/0.25',
        'area': '65/-10/35/47',
        }, f"{input_dir}/ml_fields.grb")

    server.execute({
        'type': 'fc',
        'class': 'od',
        'stream': 'oper',
        'expver': '1',
        'date': f"{startdate}/to/{enddate}",
        'time': f"{starttime}",
        'levtype': 'ml',
        'levelist': f"1/to/{max_level}",
        'step': '0/to/7/by/1',
        'param': etadot_ids,
        'grid': '0.1/0.1',
        'area': '65/-10/35/47',
        }, f"{input_dir}/etadot_fields.grb")

    server.execute({
        'class': 'od',
        'stream': 'oper',
        'expver': '1',
        'date': f"{startdate}/to/{enddate}",
        'time': f"{starttime}",
        'levtype': 'sfc',
        'param': "/".join(surface_param_ids),
        'step': '0/to/7/by/1',
        'grid': '0.1/0.1',
        'area': '65/-10/35/47',
        'type': 'fc',
        }, f"{input_dir}/sfc_fields.grb")

    server.execute({
        'class': 'od',
        'stream': 'oper',
        'expver': '1',
        'date': f"{startdate}/to/{enddate}",
        'time': f"{starttime}",
        'levtype': 'sfc',
        'param': "/".join(constant_param_ids),
        'grid': '0.1/0.1',
        'area': '65/-10/35/47',
        }, f"{input_dir}/cst_fields.grb")
