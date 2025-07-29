import os
from preflexpart.utils import setup_logger
from preflexpart.data_loading import download_ecmwf_data, load
from preflexpart.preprocessing import preprocess
from preflexpart.xarray_to_grib import write_to_grib

logger = setup_logger(__name__)

def run_preprocessing(input_dir: str, output_dir: str):
    """Run preprocessing using already downloaded ECMWF data."""
    files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]
    if not files:
        logger.info("No local files found for processing.")
        return

    ds = load(files)
    ds_out = preprocess(ds)
    write_to_grib(ds_out, output_dir)

def download_and_run_preprocessing(
    startdate: str,
    enddate: str,
    starttime: str,
    max_level: int,
    input_dir: str,
    output_dir: str
):
    """Download ECMWF data and then run the full preprocessing pipeline."""
    download_ecmwf_data(startdate, enddate, starttime, max_level, input_dir)
    run_preprocessing(input_dir, output_dir)
