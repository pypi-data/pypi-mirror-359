"""
Converts and saves xarray datasets to GRIB format
by overwiriding the metadata and convert GRIB 1 fields to GRIB 2.
"""

# Standard library
import datetime as dt
import os
import tempfile

# Third party
import pandas as pd
import xarray as xr

# Local
from preflexpart.utils import setup_logger
from preflexpart.input_fields import CONSTANT_FIELDS


logger = setup_logger(__name__)

def _parse_datetime(date, time) -> dt.datetime:
    return dt.datetime.strptime(f"{date}{time:04d}", "%Y%m%d%H%M")


def _to_timedelta(value, unit) ->  dt.timedelta:
    return pd.to_timedelta(value, unit).to_pytimedelta()

def _generate_output_key(ds_out, step):
    """
    Generate a GRIB filename from the valid time (ref. time + lead time)
     of a DataArray.

    Parameters:
    ds_out (dict): Dictionary containing `xarray.DataArray` objects.

    Returns:
    str: 'dispfYYYYMMDDHH.grib' formatted filename.
    """
    da = ds_out["u"]
    md = da.earthkit.metadata
    ref_time = _parse_datetime(md["dataDate"], md["dataTime"])
    # step = md["step"]
    unit = "h" if isinstance(step, int) else None
    step = _to_timedelta(step, unit)
    lead_time = ref_time + pd.Timedelta(step)

    valid_time_str = lead_time.strftime("%Y%m%d%H")
    return f"dispf{valid_time_str}.grib"


def write_to_grib(ds_out: dict[str, xr.DataArray], output_dir: str = "./"):
    """
    Write an xarray dataset to multiple GRIB files, one per timestep.

    This function converts and writes data from an xarray Dataset (`ds_out`) to a GRIB file.
    It ensures that GRIB 1 fields are converted to GRIB 2 before writing.
    The function will be deprecated in the future when only GRIB 2 fields are used.

    Parameters
    ----------
    ds_out : xarray.Dataset
        A dictionary where keys are variable names and values are xarray DataArrays.
    output_dir : str, optional
        The directory where the GRIB file will be saved (default is current directory

    Future Changes
    --------------
    The conversion to GRIB 2 will be removed once all fields are stored as GRIB 2.
    """

    ref_keys = ["editionNumber", "productDefinitionTemplateNumber"]
    ref_values = [2, 0]

    ref = next(
        field
        for field in ds_out.values()
        if all(
            field.earthkit.metadata.get(key) == value
            for key, value in zip(ref_keys, ref_values)
        )
    )

    os.makedirs(output_dir, exist_ok=True)

    steps = ds_out["u"].coords['step'].values

    for step in steps:
        ds_step = {}
        for name, field in ds_out.items():
            if name in CONSTANT_FIELDS:
                ds_step[name] = field
            else:
                ds_step[name] = field.sel(step=step)

        output_filename = _generate_output_key(ds_step, step)
        output_filepath = os.path.join(output_dir, output_filename)
        logger.info("Writing GRIB file to: %s", output_filepath)

        with open(output_filepath, "ab") as output_file:
            for name, field in ds_step.items():
                if field.isnull().all():
                    logger.info("Ignoring field %s - only NaN values", name)
                    continue

                if field.earthkit.metadata.get("editionNumber") == 1:
                    if name in {"lsp", "sshf", "ewss", "nsss", "cp", "ssr"}:

                        # step calculations
                        time_range = _to_timedelta(1, unit="hours")
                        step_end = pd.to_timedelta(step, unit="ns")
                        step_begin = step_end - time_range

                        md = ref.earthkit.metadata.override(
                            indicatorOfUnitOfTimeRange=0, # minute 
                            forecastTime= (step_begin / _to_timedelta(1, unit="minutes")),
                            productDefinitionTemplateNumber=8,
                            shortName=field.earthkit.metadata.get("shortName"),
                            lengthOfTimeRange=int(_to_timedelta(1, "h")/ _to_timedelta(1, "m")),
                            indicatorOfUnitForTimeRange=0,
                        )
                    else:
                        time_range = _to_timedelta(0, unit=None)
                        step_end = pd.to_timedelta(step, unit="ns")
                        step_begin = step_end - time_range

                        md = ref.earthkit.metadata.override(
                            shortName=field.earthkit.metadata.get("shortName"),
                            indicatorOfUnitOfTimeRange=0, # minute 
                            forecastTime=step_begin / _to_timedelta(1, unit="minutes"),
                        )

                    if field.earthkit.metadata.get("typeOfFirstFixedSurface") == 1:
                        md = md.override(
                            shortName=field.earthkit.metadata.get("shortName"),
                            level=0,
                        )
                else:
                    time_range = _to_timedelta(0, unit=None)
                    step_end = pd.to_timedelta(step, unit="ns")
                    step_begin = step_end - time_range

                    md = ref.earthkit.metadata.override(
                        shortName=field.earthkit.metadata.get("shortName"),
                        indicatorOfUnitOfTimeRange=0, # minute 
                        forecastTime=step_begin / _to_timedelta(1, unit="minutes"),
                    )


                # Write new metadata
                message = md._handle.get_buffer()
                field.attrs["_earthkit"] = {"message": message}

                with tempfile.NamedTemporaryFile(suffix=".grib") as tmp_file:
                    temp_filepath = tmp_file.name
                    field.earthkit.to_grib(temp_filepath)

                    with open(temp_filepath, "rb") as temp_file:
                        output_file.write(temp_file.read())

            logger.info("GRIB file saved at: %s", output_filepath)
