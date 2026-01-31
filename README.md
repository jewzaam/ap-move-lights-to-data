# ap-move-lights-to-data

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Move light frames from blink directory to data directory when calibration frames (darks, flats, and bias if needed) are available.

## Overview

This tool automates the workflow step between blinking/reviewing light frames and processing them. It only moves light frames to the data directory when matching calibration frames exist, ensuring you don't start processing data that can't be properly calibrated.

Calibration frames are searched for in the lights directory first, then in parent directories up to the source directory boundary. This supports flexible workflows where filter-specific flats are stored with lights while shared darks are in parent directories.

## Installation

### Development

```bash
make install-dev
```

### From Git

```bash
pip install git+https://github.com/jewzaam/ap-move-lights-to-data.git
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

Lights are only moved when calibration frames are found (in the lights directory or parent directories) matching these criteria:

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

The tool searches for calibration frames in the lights directory and parent directories up to the source directory. Both co-located and parent directory configurations are supported.

### Example 1: Co-located (all frames together)

```
10_Blink/
  M31/
    DATE_2024-01-15/
      light_001.fits      # Light frames
      light_002.fits
      dark_001.fits       # Dark frames (same dir)
      flat_Ha_001.fits    # Flat frames (same dir)
      bias_001.fits       # Bias (if needed)
```

### Example 2: Parent directory (shared calibration)

```
10_Blink/
  M31/
    DATE_2024-01-15/
      dark_001.fits          # Shared darks in date directory
      dark_002.fits
      FILTER_Ha/
        light_001.fits       # Light frames
        light_002.fits
        flat_Ha_001.fits     # Filter-specific flats with lights
        flat_Ha_002.fits
```

### Example 3: Mixed (flats with lights, darks in parent)

```
10_Blink/
  M31/
    DATE_2024-01-15/
      master_dark_300s.fits  # Shared master dark in parent
      FILTER_Ha/
        light_001.fits       # Lights
        flat_Ha_001.fits     # Flats with lights
      FILTER_OIII/
        light_001.fits       # Lights
        flat_OIII_001.fits   # Flats with lights
        # Both filters use same master_dark_300s.fits from parent
```

The tool searches from the lights directory upward, stopping before reaching the source directory (`10_Blink` in these examples).

### Frame Type Support

The tool recognizes both regular and MASTER frame types:
- `dark`, `DARK`, `master dark`, `MASTER DARK`
- `flat`, `FLAT`, `master flat`, `MASTER FLAT`
- `bias`, `BIAS`, `master bias`, `MASTER BIAS`

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
