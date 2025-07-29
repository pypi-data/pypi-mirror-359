import argparse
from preflexpart.runner import run_preprocessing, download_and_run_preprocessing

def main():
    parser = argparse.ArgumentParser(description="Process ECMWF data for FLEXPART.")
    parser.add_argument("--startdate", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--enddate", help="End date (YYYY-MM-DD)")
    parser.add_argument("--starttime", help="Start time (HH:MM:SS)")
    parser.add_argument("--max_level", type=int, help="Max vertical level")
    parser.add_argument("--input_dir", required=True, help="Directory with input data")
    parser.add_argument("--output_dir", required=True, help="Directory to save output")
    parser.add_argument("--download", action="store_true", help="Download ECMWF data")

    args = parser.parse_args()

    if args.download:
        if not all([args.startdate, args.enddate, args.starttime, args.max_level]):
            parser.error("Must provide startdate, enddate, starttime, and max_level when using --download.")
        download_and_run_preprocessing(
            args.startdate, args.enddate, args.starttime,
            args.max_level, args.input_dir, args.output_dir
        )
    else:
        run_preprocessing(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
