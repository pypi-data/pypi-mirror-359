"""This module provides operators for FLEXPART preprocessing."""

# Standard library
import xarray as xr
import numpy as np


def time_rate(var: xr.DataArray, dtime: np.timedelta64):
    """Compute a time rate for a given delta in time.

    It assumes the input data is an accumulated value
    between two time steps of the time coordinate

    Args:
        var: variable that contains the input data
        dtime: delta time of the desired output time rate

    """
    result = var.diff("step") * (dtime / var["step"].diff("step"))

    # TODO: The fields passed to this operator are currently in GRIB1 but will be
    # converted to GRIB2. Override the metadata accordingly.
    return xr.DataArray(
        data=result,
        attrs=var.attrs
    )

def omega_slope(
    ps: xr.DataArray, etadot: xr.DataArray, ak: xr.DataArray, bk: xr.DataArray
)-> xr.DataArray:
    """Compute the omega slope.

    Converts ECMWF etadot (deta/dt) to etadot * dp/deta, required by FLEXPART.

    Parameters
    ----------
    ps : xarray.DataArray
        Pressure (S) (not reduced) in Pa.
    etadot : xarray.DataArray
        Eta-coordinate vertical velocity (deta/dt) in s**-1.
    ak : xarray.DataArray
        Hybrid level A coefficient.
    bk : xarray.DataArray
        Hybrid level B coefficient.


    Returns
    -------
    xarray.DataArray
        Vertical velocity (pressure) in Pa s**-1.

    """
    # Surface pressure reference for omega slope
    surface_pressure_ref = 101325.0  # [Pa]

    dak_dz = ak.diff(dim="level")
    dbk_dz = bk.diff(dim="level")

    res = (
        2.0
        * etadot
        * ps
        * (dak_dz / ps + dbk_dz)
        / (dak_dz / surface_pressure_ref + dbk_dz)
    ).reduce(cumdiff, dim="level")

    return xr.DataArray(
        data=res,
        attrs=etadot.attrs,
        name="omega"
    )

def cumdiff(input_array, axis):
    """Computes the cumulative difference along a specified axis.
    This function is used to integrate the pressure differences
    over hybrid levels in the omega computation.

    Parameters
    ----------
    input_array : np.ndarray
        Input array.
    axis : int
        Axis along which to compute the cumulative difference.

    Returns
    -------
    np.ndarray
        Array with cumulative differences applied along the specified axis.
    """

    r = np.empty(np.shape(input_array))
    t = 0  # op = the ufunc being applied to A's  elements
    for i in range(np.shape(input_array)[axis]):
        t = np.take(input_array, i, axis) - t

        slices = []
        for dim in range(input_array.ndim):
            if dim == axis:
                slices.append(slice(i, i + 1))
            else:
                slices.append(slice(None))

        r[tuple(slices)] = np.expand_dims(t, axis=axis)
    return r
