# preflexpart

A Python library for pre-processing FLEXPART inputs.

## Features
- Supports preprocessing of FLEXPART meteorological input fields
- Utilizes `xarray` for data manipulation
- Integrates with ECMWF API for data retrieval (currently via MARS, with future plans to support Polytope)

## Installation

### Using Poetry
```sh
poetry install
```

## Dependencies
- Python 3.11+
- `xarray`
- `ecmwf-api-client`
- `meteodatalab` (from MeteoSwiss repository) (TODO: get rid of this dep)

## Development
Run tests using:
```sh
pytest
```

## License
This project is licensed under the terms of the LICENSE file included in this repository.

