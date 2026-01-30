"""Move light frames to data directory when calibration frames are available."""

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Optional

import ap_common

from . import config
from .matching import get_light_group_metadata, has_calibration_frames


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
    calibration_dirs: List[str],
    debug: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Process light directories and move those with calibration frames.

    Args:
        source_dir: Source directory containing lights (e.g., 10_Blink)
        dest_dir: Destination directory (e.g., 20_Data)
        calibration_dirs: List of directories containing calibration frames
        debug: Enable debug output
        dry_run: If True, only print what would be done

    Returns:
        Dict with counts: moved, skipped_no_darks, skipped_no_flats, errors
    """
    results = {
        "moved": 0,
        "skipped_no_darks": 0,
        "skipped_no_flats": 0,
        "skipped_no_metadata": 0,
        "errors": 0,
    }

    source_path = Path(ap_common.replace_env_vars(source_dir))
    dest_path = Path(ap_common.replace_env_vars(dest_dir))

    # Find all light directories
    light_dirs = find_light_directories(source_dir, debug)

    if not light_dirs:
        print(f"No light directories found in {source_path}")
        return results

    print(f"Found {len(light_dirs)} light directories to process")

    for light_dir in light_dirs:
        relative_path = get_target_from_path(light_dir, source_dir)
        print(f"\nProcessing: {relative_path}")

        # Get representative metadata for this light group
        metadata = get_light_group_metadata(light_dir, debug)

        if not metadata:
            print("  SKIP: No metadata found")
            results["skipped_no_metadata"] += 1
            continue

        if debug:
            print(f"  Metadata: {metadata}")

        # Check for calibration frames
        has_darks, has_flats, dark_count, flat_count = has_calibration_frames(
            metadata, calibration_dirs, debug
        )

        if not has_darks:
            print(f"  SKIP: No matching darks found")
            results["skipped_no_darks"] += 1
            continue

        if not has_flats:
            print(f"  SKIP: No matching flats found")
            results["skipped_no_flats"] += 1
            continue

        print(f"  Found {dark_count} darks and {flat_count} flats")

        # Move the directory
        dest_full = dest_path / relative_path
        success = move_directory(light_dir, str(dest_full), debug, dry_run)

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
        description="Move light frames to data directory when calibration frames exist"
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
        "--calibration-dir",
        "-c",
        action="append",
        dest="calibration_dirs",
        help="Directory to search for calibration frames (can specify multiple)",
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

    # Use source directory as calibration search if not specified
    calibration_dirs = args.calibration_dirs
    if not calibration_dirs:
        # Default: search in common calibration locations relative to source
        source_parent = Path(ap_common.replace_env_vars(args.source_dir)).parent
        calibration_dirs = [str(source_parent)]
        print(f"No calibration directories specified, searching in: {source_parent}")

    print(f"Source directory: {args.source_dir}")
    print(f"Destination directory: {args.dest_dir}")
    print(f"Calibration directories: {calibration_dirs}")

    if args.dry_run:
        print("\n*** DRY RUN - No files will be moved ***\n")

    results = process_light_directories(
        args.source_dir,
        args.dest_dir,
        calibration_dirs,
        args.debug,
        args.dry_run,
    )

    # Print summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Moved:              {results['moved']}")
    print(f"  Skipped (no darks): {results['skipped_no_darks']}")
    print(f"  Skipped (no flats): {results['skipped_no_flats']}")
    print(f"  Skipped (no meta):  {results['skipped_no_metadata']}")
    print(f"  Errors:             {results['errors']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
