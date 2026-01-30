"""Tests for move_lights_to_data module."""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ap_move_lights_to_data import move_lights_to_data


class TestFindLightDirectories:
    """Tests for find_light_directories function."""

    def test_finds_directories_with_fits_files(self, tmp_path):
        """Verify directories containing FITS files are found."""
        # Create test structure
        light_dir = tmp_path / "10_Blink" / "M31" / "DATE_2024-01-15"
        light_dir.mkdir(parents=True)
        (light_dir / "light_001.fits").touch()

        result = move_lights_to_data.find_light_directories(
            str(tmp_path / "10_Blink")
        )

        assert len(result) == 1
        assert str(light_dir) in result

    def test_finds_directories_with_xisf_files(self, tmp_path):
        """Verify directories containing XISF files are found."""
        light_dir = tmp_path / "10_Blink" / "NGC7000"
        light_dir.mkdir(parents=True)
        (light_dir / "light_001.xisf").touch()

        result = move_lights_to_data.find_light_directories(
            str(tmp_path / "10_Blink")
        )

        assert len(result) == 1

    def test_returns_empty_for_no_images(self, tmp_path):
        """Verify empty list when no image files exist."""
        empty_dir = tmp_path / "10_Blink" / "empty"
        empty_dir.mkdir(parents=True)
        (empty_dir / "readme.txt").touch()

        result = move_lights_to_data.find_light_directories(
            str(tmp_path / "10_Blink")
        )

        assert len(result) == 0


class TestGetTargetFromPath:
    """Tests for get_target_from_path function."""

    def test_extracts_relative_path(self, tmp_path):
        """Verify relative path extraction."""
        source = str(tmp_path / "10_Blink")
        light_dir = str(tmp_path / "10_Blink" / "M31" / "DATE_2024-01-15")

        result = move_lights_to_data.get_target_from_path(light_dir, source)

        assert result == os.path.join("M31", "DATE_2024-01-15")

    def test_handles_nested_structure(self, tmp_path):
        """Verify deeply nested structure extraction."""
        source = str(tmp_path / "10_Blink")
        light_dir = str(
            tmp_path / "10_Blink" / "M31" / "DATE_2024-01-15" / "FILTER_Ha_EXP_300"
        )

        result = move_lights_to_data.get_target_from_path(light_dir, source)

        assert "M31" in result
        assert "FILTER_Ha_EXP_300" in result


class TestMoveDirectory:
    """Tests for move_directory function."""

    def test_moves_directory_contents(self, tmp_path):
        """Verify directory is moved with contents."""
        source = tmp_path / "source" / "target"
        source.mkdir(parents=True)
        (source / "file1.fits").touch()
        (source / "file2.fits").touch()

        dest = tmp_path / "dest" / "target"

        result = move_lights_to_data.move_directory(str(source), str(dest))

        assert result is True
        assert dest.exists()
        assert (dest / "file1.fits").exists()
        assert not source.exists()

    def test_dry_run_does_not_move(self, tmp_path):
        """Verify dry run does not actually move files."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.fits").touch()

        dest = tmp_path / "dest"

        result = move_lights_to_data.move_directory(
            str(source), str(dest), dry_run=True
        )

        assert result is True
        assert source.exists()
        assert not dest.exists()

    def test_creates_parent_directories(self, tmp_path):
        """Verify parent directories are created."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.fits").touch()

        dest = tmp_path / "deep" / "nested" / "path" / "dest"

        result = move_lights_to_data.move_directory(str(source), str(dest))

        assert result is True
        assert dest.exists()


class TestProcessLightDirectories:
    """Tests for process_light_directories function."""

    @patch("ap_move_lights_to_data.move_lights_to_data.has_calibration_frames")
    @patch("ap_move_lights_to_data.move_lights_to_data.get_light_group_metadata")
    @patch("ap_move_lights_to_data.move_lights_to_data.find_light_directories")
    def test_skips_when_no_darks(
        self, mock_find, mock_metadata, mock_calibration, tmp_path
    ):
        """Verify directories are skipped when no darks exist."""
        mock_find.return_value = [str(tmp_path / "light_dir")]
        mock_metadata.return_value = {"type": "light"}
        mock_calibration.return_value = (False, True, 0, 5)  # No darks, has flats

        results = move_lights_to_data.process_light_directories(
            str(tmp_path / "10_Blink"),
            str(tmp_path / "20_Data"),
            [str(tmp_path / "calibration")],
        )

        assert results["skipped_no_darks"] == 1
        assert results["moved"] == 0

    @patch("ap_move_lights_to_data.move_lights_to_data.has_calibration_frames")
    @patch("ap_move_lights_to_data.move_lights_to_data.get_light_group_metadata")
    @patch("ap_move_lights_to_data.move_lights_to_data.find_light_directories")
    def test_skips_when_no_flats(
        self, mock_find, mock_metadata, mock_calibration, tmp_path
    ):
        """Verify directories are skipped when no flats exist."""
        mock_find.return_value = [str(tmp_path / "light_dir")]
        mock_metadata.return_value = {"type": "light"}
        mock_calibration.return_value = (True, False, 10, 0)  # Has darks, no flats

        results = move_lights_to_data.process_light_directories(
            str(tmp_path / "10_Blink"),
            str(tmp_path / "20_Data"),
            [str(tmp_path / "calibration")],
        )

        assert results["skipped_no_flats"] == 1
        assert results["moved"] == 0

    @patch("ap_move_lights_to_data.move_lights_to_data.ap_common")
    @patch("ap_move_lights_to_data.move_lights_to_data.move_directory")
    @patch("ap_move_lights_to_data.move_lights_to_data.has_calibration_frames")
    @patch("ap_move_lights_to_data.move_lights_to_data.get_light_group_metadata")
    @patch("ap_move_lights_to_data.move_lights_to_data.find_light_directories")
    def test_moves_when_calibration_exists(
        self, mock_find, mock_metadata, mock_calibration, mock_move, mock_ap_common, tmp_path
    ):
        """Verify directories are moved when calibration frames exist."""
        source_dir = tmp_path / "10_Blink"
        light_dir = source_dir / "M31" / "DATE_2024"
        light_dir.mkdir(parents=True)

        mock_find.return_value = [str(light_dir)]
        mock_metadata.return_value = {"type": "light"}
        mock_calibration.return_value = (True, True, 10, 5)  # Has both
        mock_move.return_value = True
        mock_ap_common.replace_env_vars.side_effect = lambda x: x

        results = move_lights_to_data.process_light_directories(
            str(source_dir),
            str(tmp_path / "20_Data"),
            [str(tmp_path / "calibration")],
        )

        assert results["moved"] == 1
        mock_move.assert_called_once()
