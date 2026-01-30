"""Calibration frame matching logic."""

from typing import Dict, List, Optional, Any
import ap_common

from . import config


def find_matching_darks(
    light_metadata: Dict[str, Any],
    calibration_dirs: List[str],
    debug: bool = False,
) -> List[str]:
    """
    Find dark frames that match the light frame settings.

    Args:
        light_metadata: Metadata dict for a light frame
        calibration_dirs: List of directories to search for darks
        debug: Enable debug output

    Returns:
        List of matching dark file paths
    """
    # Build filter criteria from light metadata
    filters = {config.KEYWORD_TYPE: config.TYPE_DARK}

    for key in config.DARK_MATCH_KEYWORDS:
        if key in light_metadata and light_metadata[key] is not None:
            filters[key] = light_metadata[key]

    if debug:
        print(f"  Searching for darks with filters: {filters}")

    # Search for matching darks
    matching = ap_common.get_filtered_metadata(
        dirs=calibration_dirs,
        patterns=config.SUPPORTED_EXTENSIONS,
        required_properties=[config.KEYWORD_TYPE] + config.DARK_MATCH_KEYWORDS,
        filters=filters,
        show_status=debug,
    )

    return list(matching.keys())


def find_matching_flats(
    light_metadata: Dict[str, Any],
    calibration_dirs: List[str],
    debug: bool = False,
) -> List[str]:
    """
    Find flat frames that match the light frame settings.

    Args:
        light_metadata: Metadata dict for a light frame
        calibration_dirs: List of directories to search for flats
        debug: Enable debug output

    Returns:
        List of matching flat file paths
    """
    # Build filter criteria from light metadata
    filters = {config.KEYWORD_TYPE: config.TYPE_FLAT}

    for key in config.FLAT_MATCH_KEYWORDS:
        if key in light_metadata and light_metadata[key] is not None:
            filters[key] = light_metadata[key]

    if debug:
        print(f"  Searching for flats with filters: {filters}")

    # Search for matching flats
    matching = ap_common.get_filtered_metadata(
        dirs=calibration_dirs,
        patterns=config.SUPPORTED_EXTENSIONS,
        required_properties=[config.KEYWORD_TYPE] + config.FLAT_MATCH_KEYWORDS,
        filters=filters,
        show_status=debug,
    )

    return list(matching.keys())


def has_calibration_frames(
    light_metadata: Dict[str, Any],
    calibration_dirs: List[str],
    debug: bool = False,
) -> tuple:
    """
    Check if calibration frames (darks and flats) exist for the given light.

    Args:
        light_metadata: Metadata dict for a light frame
        calibration_dirs: List of directories to search for calibration frames
        debug: Enable debug output

    Returns:
        Tuple of (has_darks, has_flats, dark_count, flat_count)
    """
    darks = find_matching_darks(light_metadata, calibration_dirs, debug)
    flats = find_matching_flats(light_metadata, calibration_dirs, debug)

    return (len(darks) > 0, len(flats) > 0, len(darks), len(flats))


def get_light_group_metadata(
    light_dir: str,
    debug: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Get representative metadata for a directory of light frames.

    Extracts metadata from the first light frame found in the directory.

    Args:
        light_dir: Directory containing light frames
        debug: Enable debug output

    Returns:
        Metadata dict for the light group, or None if no lights found
    """
    # Get metadata from all files in the directory
    metadata = ap_common.get_metadata(
        dirs=[light_dir],
        patterns=config.SUPPORTED_EXTENSIONS,
        required_properties=config.LIGHT_REQUIRED_KEYWORDS,
        show_status=debug,
    )

    if not metadata:
        return None

    # Filter for light frames only
    lights = {
        k: v
        for k, v in metadata.items()
        if v.get(config.KEYWORD_TYPE, "").lower() == config.TYPE_LIGHT
    }

    if not lights:
        # If no explicit light frames, assume all are lights
        lights = metadata

    # Return the first light's metadata as representative
    first_light = next(iter(lights.values()))
    return first_light
