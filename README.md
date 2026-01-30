# ap-move-lights-to-data

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Move light frames from blink directory to data directory when calibration frames (darks and flats) are available.

## Overview

This tool automates the workflow step between blinking/reviewing light frames and processing them. It only moves light frames to the data directory when matching calibration frames exist, ensuring you don't start processing data that can't be properly calibrated.

## Installation

```bash
pip install git+https://github.com/jewzaam/ap-move-lights-to-data.git
```

Or for development:

```bash
git clone https://github.com/jewzaam/ap-move-lights-to-data.git
cd ap-move-lights-to-data
make install-dev
```

## Usage

```bash
python -m ap_move_lights_to_data <source_dir> <dest_dir> [options]
```

### Arguments

- `source_dir`: Source directory containing light frames (typically `10_Blink`)
- `dest_dir`: Destination directory for lights with calibration (typically `20_Data`)

### Options

- `-c, --calibration-dir`: Directory to search for calibration frames (can specify multiple)
- `-d, --debug`: Enable debug output
- `-n, --dry-run`: Show what would be done without actually moving files

### Example

```bash
# Move lights from 10_Blink to 20_Data, searching for calibration in parent directory
python -m ap_move_lights_to_data \
    "/astrophotography/RedCat51@f4.9+ASI2600MM/10_Blink" \
    "/astrophotography/RedCat51@f4.9+ASI2600MM/20_Data" \
    -c "/astrophotography/calibration"

# Dry run to see what would be moved
python -m ap_move_lights_to_data \
    "10_Blink" \
    "20_Data" \
    -c "../calibration" \
    --dry-run
```

## Calibration Matching

Lights are only moved when **both** darks and flats are found matching these criteria:

### Dark Matching
- Camera
- Set temperature
- Gain
- Offset
- Readout mode

### Flat Matching
- Camera
- Set temperature
- Gain
- Offset
- Readout mode
- Filter

## Directory Structure

The tool preserves the directory structure when moving:

```
10_Blink/
  M31/
    DATE_2024-01-15/
      FILTER_Ha_EXP_300/
        light_001.fits
        light_002.fits

# Becomes (if calibration exists):

20_Data/
  M31/
    DATE_2024-01-15/
      FILTER_Ha_EXP_300/
        light_001.fits
        light_002.fits
```

## Dependencies

- [ap-common](https://github.com/jewzaam/ap-common): Shared astrophotography utilities

## Development

```bash
# Install dev dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-coverage

# Format code
make format

# Lint code
make lint
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details