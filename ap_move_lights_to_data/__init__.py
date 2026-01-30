"""ap-move-lights-to-data: Move lights to data directory when calibration frames exist."""

from .config import (
    KEYWORD_TYPE,
    KEYWORD_CAMERA,
    KEYWORD_SETTEMP,
    KEYWORD_GAIN,
    KEYWORD_OFFSET,
    KEYWORD_READOUTMODE,
    KEYWORD_EXPOSURESECONDS,
    KEYWORD_DATE,
    KEYWORD_FILTER,
    TYPE_LIGHT,
    TYPE_DARK,
    TYPE_FLAT,
    TYPE_BIAS,
    LIGHT_REQUIRED_KEYWORDS,
    DARK_MATCH_KEYWORDS,
    FLAT_MATCH_KEYWORDS,
    DEFAULT_BLINK_DIR,
    DEFAULT_DATA_DIR,
    SUPPORTED_EXTENSIONS,
)

from .matching import (
    get_frames_by_type,
    find_matching_darks,
    find_matching_flats,
    find_matching_bias,
    check_calibration_status,
)

from .move_lights_to_data import (
    find_light_directories,
    get_target_from_path,
    move_directory,
    process_light_directories,
    main,
)

__all__ = [
    # Config constants
    "KEYWORD_TYPE",
    "KEYWORD_CAMERA",
    "KEYWORD_SETTEMP",
    "KEYWORD_GAIN",
    "KEYWORD_OFFSET",
    "KEYWORD_READOUTMODE",
    "KEYWORD_EXPOSURESECONDS",
    "KEYWORD_DATE",
    "KEYWORD_FILTER",
    "TYPE_LIGHT",
    "TYPE_DARK",
    "TYPE_FLAT",
    "TYPE_BIAS",
    "LIGHT_REQUIRED_KEYWORDS",
    "DARK_MATCH_KEYWORDS",
    "FLAT_MATCH_KEYWORDS",
    "DEFAULT_BLINK_DIR",
    "DEFAULT_DATA_DIR",
    "SUPPORTED_EXTENSIONS",
    # Matching functions
    "get_frames_by_type",
    "find_matching_darks",
    "find_matching_flats",
    "find_matching_bias",
    "check_calibration_status",
    # Main functions
    "find_light_directories",
    "get_target_from_path",
    "move_directory",
    "process_light_directories",
    "main",
]
