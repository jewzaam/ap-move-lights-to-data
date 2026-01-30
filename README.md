# ap-move-lights-to-data

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Move light frames from blink directory to data directory when calibration frames (darks, flats, and bias if needed) are available in the same directory.

## Overview

This tool automates the workflow step between blinking/reviewing light frames and processing them. It only moves light frames to the data directory when matching calibration frames exist **in the same directory**, ensuring you don't start processing data that can't be properly calibrated.

**Key requirement**: Calibration frames (darks, flats, bias) must be co-located with the light frames in the same directory structure.

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

- `-d, --debug`: Enable debug output
- `-n, --dry-run`: Show what would be done without actually moving files

### Example

```bash
# Move lights from 10_Blink to 20_Data
python -m ap_move_lights_to_data \
    "/astrophotography/RedCat51@f4.9+ASI2600MM/10_Blink" \
    "/astrophotography/RedCat51@f4.9+ASI2600MM/20_Data"

# Dry run to see what would be moved
python -m ap_move_lights_to_data \
    "10_Blink" \
    "20_Data" \
    --dry-run
```

## Calibration Requirements

Lights are only moved when calibration frames are found **in the same directory** matching these criteria:

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

### Bias Requirement

Bias frames are **only required** when the dark exposure time does not match the light exposure time. This is because darks with mismatched exposure times need bias subtraction for proper scaling.

If dark exposure matches light exposure: **No bias required**
If dark exposure differs from light exposure: **Bias required**

## Directory Structure

The tool expects calibration frames to be in the same directory as lights:

```
10_Blink/
  M31/
    accept/
      DATE_2024-01-15/
        light_001.fits      # Light frames
        light_002.fits
        dark_001.fits       # Dark frames (same dir)
        dark_002.fits
        flat_Ha_001.fits    # Flat frames (same dir)
        flat_Ha_002.fits
        bias_001.fits       # Bias (only if dark exp != light exp)

# Becomes (if calibration complete):

20_Data/
  M31/
    accept/
      DATE_2024-01-15/
        light_001.fits
        light_002.fits
        dark_001.fits
        dark_002.fits
        flat_Ha_001.fits
        flat_Ha_002.fits
        bias_001.fits
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
