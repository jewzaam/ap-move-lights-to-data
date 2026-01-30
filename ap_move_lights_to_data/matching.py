"""Calibration frame matching logic."""

from typing import Dict, List, Any, Tuple
import ap_common

from . import config


def get_frames_by_type(
    directory: str,
    debug: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Get all frames from a directory grouped by type.

    Args:
        directory: Directory to scan for frames
        debug: Enable debug output

    Returns:
        Dict with keys 'light', 'dark', 'flat', 'bias' containing metadata dicts
    """
    # Get metadata from all files in the directory
    all_metadata = ap_common.get_metadata(
        dirs=[directory],
        patterns=config.SUPPORTED_EXTENSIONS,
        required_properties=[config.KEYWORD_TYPE],
        show_status=debug,
    )

    # Group by type
    frames = {
        config.TYPE_LIGHT: {},
        config.TYPE_DARK: {},
        config.TYPE_FLAT: {},
        config.TYPE_BIAS: {},
    }

    for filepath, metadata in all_metadata.items():
        frame_type = str(metadata.get(config.KEYWORD_TYPE, "")).lower()
        if frame_type in frames:
            frames[frame_type][filepath] = metadata

    if debug:
        for frame_type, files in frames.items():
            print(f"  Found {len(files)} {frame_type} frames")

    return frames


def find_matching_darks(
    light_metadata: Dict[str, Any],
    dark_frames: Dict[str, Dict[str, Any]],
    debug: bool = False,
) -> Tuple[List[str], bool]:
    """
    Find dark frames that match the light frame settings.

    Args:
        light_metadata: Metadata dict for a light frame
        dark_frames: Dict of dark frame metadata keyed by filepath
        debug: Enable debug output

    Returns:
        Tuple of (list of matching dark file paths, exposure_matches)
        exposure_matches is True if any dark has same exposure as light
    """
    matching = []
    exposure_matches = False
    light_exposure = light_metadata.get(config.KEYWORD_EXPOSURESECONDS)

    for filepath, dark_meta in dark_frames.items():
        # Check all match keywords
        matches = True
        for key in config.DARK_MATCH_KEYWORDS:
            light_val = light_metadata.get(key)
            dark_val = dark_meta.get(key)
            if light_val is not None and dark_val is not None:
                if str(light_val).lower() != str(dark_val).lower():
                    matches = False
                    break

        if matches:
            matching.append(filepath)
            # Check if exposure matches
            dark_exposure = dark_meta.get(config.KEYWORD_EXPOSURESECONDS)
            if light_exposure and dark_exposure:
                try:
                    if float(light_exposure) == float(dark_exposure):
                        exposure_matches = True
                except (ValueError, TypeError):
                    pass

    if debug:
        print(f"  Found {len(matching)} matching darks, exposure_matches={exposure_matches}")

    return matching, exposure_matches


def find_matching_flats(
    light_metadata: Dict[str, Any],
    flat_frames: Dict[str, Dict[str, Any]],
    debug: bool = False,
) -> List[str]:
    """
    Find flat frames that match the light frame settings.

    Args:
        light_metadata: Metadata dict for a light frame
        flat_frames: Dict of flat frame metadata keyed by filepath
        debug: Enable debug output

    Returns:
        List of matching flat file paths
    """
    matching = []

    for filepath, flat_meta in flat_frames.items():
        # Check all match keywords
        matches = True
        for key in config.FLAT_MATCH_KEYWORDS:
            light_val = light_metadata.get(key)
            flat_val = flat_meta.get(key)
            if light_val is not None and flat_val is not None:
                if str(light_val).lower() != str(flat_val).lower():
                    matches = False
                    break

        if matches:
            matching.append(filepath)

    if debug:
        print(f"  Found {len(matching)} matching flats")

    return matching


def find_matching_bias(
    light_metadata: Dict[str, Any],
    bias_frames: Dict[str, Dict[str, Any]],
    debug: bool = False,
) -> List[str]:
    """
    Find bias frames that match the light frame settings.

    Args:
        light_metadata: Metadata dict for a light frame
        bias_frames: Dict of bias frame metadata keyed by filepath
        debug: Enable debug output

    Returns:
        List of matching bias file paths
    """
    matching = []

    # Bias matches on same keywords as dark (minus exposure)
    for filepath, bias_meta in bias_frames.items():
        matches = True
        for key in config.DARK_MATCH_KEYWORDS:
            light_val = light_metadata.get(key)
            bias_val = bias_meta.get(key)
            if light_val is not None and bias_val is not None:
                if str(light_val).lower() != str(bias_val).lower():
                    matches = False
                    break

        if matches:
            matching.append(filepath)

    if debug:
        print(f"  Found {len(matching)} matching bias frames")

    return matching


def check_calibration_status(
    directory: str,
    debug: bool = False,
) -> Dict[str, Any]:
    """
    Check calibration status for a directory containing lights.

    Calibration frames must be in the same directory as the lights.
    Bias is only required if dark exposure doesn't match light exposure.

    Args:
        directory: Directory containing light frames and calibration
        debug: Enable debug output

    Returns:
        Dict with:
            - has_lights: bool
            - has_darks: bool
            - has_flats: bool
            - has_bias: bool
            - needs_bias: bool (True if dark exposure != light exposure)
            - is_complete: bool (has all required calibration)
            - light_count, dark_count, flat_count, bias_count: int
            - light_metadata: representative light metadata
            - reason: str explaining why incomplete (if applicable)
    """
    result = {
        "has_lights": False,
        "has_darks": False,
        "has_flats": False,
        "has_bias": False,
        "needs_bias": False,
        "is_complete": False,
        "light_count": 0,
        "dark_count": 0,
        "flat_count": 0,
        "bias_count": 0,
        "light_metadata": None,
        "reason": None,
    }

    # Get all frames by type
    frames = get_frames_by_type(directory, debug)

    lights = frames[config.TYPE_LIGHT]
    darks = frames[config.TYPE_DARK]
    flats = frames[config.TYPE_FLAT]
    bias = frames[config.TYPE_BIAS]

    result["light_count"] = len(lights)
    result["has_lights"] = len(lights) > 0

    if not lights:
        result["reason"] = "No light frames found"
        return result

    # Get representative light metadata
    light_metadata = next(iter(lights.values()))
    result["light_metadata"] = light_metadata

    # Find matching darks
    matching_darks, exposure_matches = find_matching_darks(
        light_metadata, darks, debug
    )
    result["dark_count"] = len(matching_darks)
    result["has_darks"] = len(matching_darks) > 0

    if not matching_darks:
        result["reason"] = "No matching dark frames"
        return result

    # Determine if bias is needed
    result["needs_bias"] = not exposure_matches

    # Find matching flats
    matching_flats = find_matching_flats(light_metadata, flats, debug)
    result["flat_count"] = len(matching_flats)
    result["has_flats"] = len(matching_flats) > 0

    if not matching_flats:
        result["reason"] = "No matching flat frames"
        return result

    # Check bias if needed
    if result["needs_bias"]:
        matching_bias = find_matching_bias(light_metadata, bias, debug)
        result["bias_count"] = len(matching_bias)
        result["has_bias"] = len(matching_bias) > 0

        if not matching_bias:
            result["reason"] = "Dark exposure mismatch requires bias, but none found"
            return result

    # All checks passed
    result["is_complete"] = True
    return result
