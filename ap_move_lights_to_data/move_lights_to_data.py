"""Move light frames to data directory when calibration frames are available."""

import argparse
import os
import shutil
from pathlib import Path
from typing import List

import ap_common

from . import config
from .matching import check_calibration_status


def find_light_directories(
    source_dir: str,
    debug: bool = False,
) -> List[str]:
    """
    Find directories containing light frames in the source directory.

    Searches for directories that contain FITS/XISF files under the source.
    Returns the leaf directories containing actual image files.

    Args:
        source_dir: Root directory to search (e.g., 10_Blink)
        debug: Enable debug output

    Returns:
        List of directory paths containing light frames
    """
    source_path = Path(ap_common.replace_env_vars(source_dir))
    light_dirs = set()

    if debug:
        print(f"Searching for light directories in: {source_path}")

    # Walk through the directory tree
    for root, dirs, files in os.walk(source_path):
        # Check if this directory contains any supported files
        has_images = False
        for ext in ["fits", "fit", "xisf"]:
            if any(f.lower().endswith(f".{ext}") for f in files):
                has_images = True
                break

        if has_images:
            light_dirs.add(root)

    result = sorted(light_dirs)
    if debug:
        print(f"Found {len(result)} directories with image files")

    return result


def get_target_from_path(light_dir: str, source_dir: str) -> str:
    """
    Extract the target/structure path relative to source directory.

    Args:
        light_dir: Full path to light directory
        source_dir: Source root directory (e.g., 10_Blink path)

    Returns:
        Relative path structure (e.g., "M31/DATE_2024-01-15/...")
    """
    source_path = Path(ap_common.replace_env_vars(source_dir))
    light_path = Path(light_dir)

    try:
        relative = light_path.relative_to(source_path)
        return str(relative)
    except ValueError:
        # Fallback to just the directory name
        return light_path.name


def move_directory(
    source: str,
    dest: str,
    debug: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Move a directory and its contents to a new location.

    Args:
        source: Source directory path
        dest: Destination directory path
        debug: Enable debug output
        dry_run: If True, only print what would be done

    Returns:
        True if successful (or dry run), False otherwise
    """
    source_path = Path(source)
    dest_path = Path(dest)

    if debug or dry_run:
        print(f"  Moving: {source_path}")
        print(f"      To: {dest_path}")

    if dry_run:
        return True

    try:
        # Create parent directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the directory
        shutil.move(str(source_path), str(dest_path))
        return True
    except Exception as e:
        print(f"  ERROR moving directory: {e}")
        return False


def process_light_directories(
    source_dir: str,
    dest_dir: str,
    debug: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Process light directories and move those with calibration frames.

    Calibration frames (darks, flats, and bias if needed) must be in the
    same directory as the light frames.

    Args:
        source_dir: Source directory containing lights (e.g., 10_Blink)
        dest_dir: Destination directory (e.g., 20_Data)
        debug: Enable debug output
        dry_run: If True, only print what would be done

    Returns:
        Dict with counts: moved, skipped (by reason), errors
    """
    results = {
        "moved": 0,
        "skipped_no_lights": 0,
        "skipped_no_darks": 0,
        "skipped_no_flats": 0,
        "skipped_no_bias": 0,
        "errors": 0,
    }

    source_path = Path(ap_common.replace_env_vars(source_dir))
    dest_path = Path(ap_common.replace_env_vars(dest_dir))

    # Find all directories with image files
    image_dirs = find_light_directories(source_dir, debug)

    if not image_dirs:
        print(f"No image directories found in {source_path}")
        return results

    print(f"Found {len(image_dirs)} directories to check")

    for image_dir in image_dirs:
        relative_path = get_target_from_path(image_dir, source_dir)
        print(f"\nProcessing: {relative_path}")

        # Check calibration status (frames must be in same directory)
        status = check_calibration_status(image_dir, debug)

        if not status["has_lights"]:
            print("  SKIP: No light frames found")
            results["skipped_no_lights"] += 1
            continue

        if debug:
            print(f"  Lights: {status['light_count']}, "
                  f"Darks: {status['dark_count']}, "
                  f"Flats: {status['flat_count']}, "
                  f"Bias: {status['bias_count']}")
            if status["needs_bias"]:
                print("  Note: Bias required (dark exposure != light exposure)")

        if not status["is_complete"]:
            reason = status["reason"]
            print(f"  SKIP: {reason}")

            # Track specific skip reason
            if "dark" in reason.lower():
                results["skipped_no_darks"] += 1
            elif "flat" in reason.lower():
                results["skipped_no_flats"] += 1
            elif "bias" in reason.lower():
                results["skipped_no_bias"] += 1
            continue

        print(f"  Calibration complete: {status['dark_count']} darks, "
              f"{status['flat_count']} flats"
              + (f", {status['bias_count']} bias" if status["needs_bias"] else ""))

        # Move the directory
        dest_full = dest_path / relative_path
        success = move_directory(image_dir, str(dest_full), debug, dry_run)

        if success:
            results["moved"] += 1
            print(f"  MOVED to {dest_full}")
        else:
            results["errors"] += 1

    # Cleanup empty directories in source
    if not dry_run and results["moved"] > 0:
        print(f"\nCleaning up empty directories in {source_path}")
        ap_common.delete_empty_directories(str(source_path), debug=debug)

    return results


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Move light frames to data directory when calibration frames exist. "
                    "Calibration frames (darks, flats, bias) must be in the same directory "
                    "as the light frames."
    )

    parser.add_argument(
        "source_dir",
        help=f"Source directory containing lights (default name: {config.DEFAULT_BLINK_DIR})",
    )

    parser.add_argument(
        "dest_dir",
        help=f"Destination directory for lights (default name: {config.DEFAULT_DATA_DIR})",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output",
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without actually moving files",
    )

    args = parser.parse_args()

    print(f"Source directory: {args.source_dir}")
    print(f"Destination directory: {args.dest_dir}")
    print("Calibration frames must be co-located with lights")

    if args.dry_run:
        print("\n*** DRY RUN - No files will be moved ***\n")

    results = process_light_directories(
        args.source_dir,
        args.dest_dir,
        args.debug,
        args.dry_run,
    )

    # Print summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Moved:              {results['moved']}")
    print(f"  Skipped (no lights):{results['skipped_no_lights']}")
    print(f"  Skipped (no darks): {results['skipped_no_darks']}")
    print(f"  Skipped (no flats): {results['skipped_no_flats']}")
    print(f"  Skipped (no bias):  {results['skipped_no_bias']}")
    print(f"  Errors:             {results['errors']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
