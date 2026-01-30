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
    find_matching_darks,
    find_matching_flats,
    has_calibration_frames,
    get_light_group_metadata,
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
    "find_matching_darks",
    "find_matching_flats",
    "has_calibration_frames",
    "get_light_group_metadata",
    # Main functions
    "find_light_directories",
    "get_target_from_path",
    "move_directory",
    "process_light_directories",
    "main",
]
