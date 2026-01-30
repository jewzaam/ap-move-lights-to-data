"""Configuration constants for ap-move-lights-to-data."""

# Normalized keyword names (matching ap-common normalization)
KEYWORD_TYPE = "type"
KEYWORD_CAMERA = "camera"
KEYWORD_SETTEMP = "settemp"
KEYWORD_GAIN = "gain"
KEYWORD_OFFSET = "offset"
KEYWORD_READOUTMODE = "readoutmode"
KEYWORD_EXPOSURESECONDS = "exposureseconds"
KEYWORD_DATE = "date"
KEYWORD_FILTER = "filter"

# Frame types
TYPE_LIGHT = "light"
TYPE_DARK = "dark"
TYPE_FLAT = "flat"
TYPE_BIAS = "bias"

# Required keywords for matching lights to calibration frames
LIGHT_REQUIRED_KEYWORDS = [
    KEYWORD_TYPE,
    KEYWORD_CAMERA,
    KEYWORD_SETTEMP,
    KEYWORD_GAIN,
    KEYWORD_OFFSET,
    KEYWORD_READOUTMODE,
    KEYWORD_EXPOSURESECONDS,
    KEYWORD_FILTER,
]

# Keywords for matching darks to lights (excluding exposure for flexibility)
DARK_MATCH_KEYWORDS = [
    KEYWORD_CAMERA,
    KEYWORD_SETTEMP,
    KEYWORD_GAIN,
    KEYWORD_OFFSET,
    KEYWORD_READOUTMODE,
]

# Keywords for matching flats to lights
FLAT_MATCH_KEYWORDS = [
    KEYWORD_CAMERA,
    KEYWORD_SETTEMP,
    KEYWORD_GAIN,
    KEYWORD_OFFSET,
    KEYWORD_READOUTMODE,
    KEYWORD_FILTER,
]

# Default directory names
DEFAULT_BLINK_DIR = "10_Blink"
DEFAULT_DATA_DIR = "20_Data"

# Supported file extensions
SUPPORTED_EXTENSIONS = ["*.fits", "*.fit", "*.xisf"]
