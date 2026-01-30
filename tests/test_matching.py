"""Tests for matching module."""

import pytest
from unittest.mock import patch, MagicMock

from ap_move_lights_to_data import matching, config


class TestFindMatchingDarks:
    """Tests for find_matching_darks function."""

    @patch("ap_move_lights_to_data.matching.ap_common")
    def test_builds_correct_filters(self, mock_ap_common):
        """Verify correct filter criteria are built from light metadata."""
        mock_ap_common.get_filtered_metadata.return_value = {}

        light_metadata = {
            config.KEYWORD_CAMERA: "ASI2600MM",
            config.KEYWORD_SETTEMP: "-10",
            config.KEYWORD_GAIN: "100",
            config.KEYWORD_OFFSET: "50",
            config.KEYWORD_READOUTMODE: "0",
            config.KEYWORD_FILTER: "Ha",
        }

        matching.find_matching_darks(light_metadata, ["/calibration"])

        # Verify the call was made with proper filters
        call_args = mock_ap_common.get_filtered_metadata.call_args
        filters = call_args.kwargs["filters"]

        assert filters[config.KEYWORD_TYPE] == config.TYPE_DARK
        assert filters[config.KEYWORD_CAMERA] == "ASI2600MM"
        assert filters[config.KEYWORD_SETTEMP] == "-10"
        assert filters[config.KEYWORD_GAIN] == "100"

    @patch("ap_move_lights_to_data.matching.ap_common")
    def test_returns_matching_files(self, mock_ap_common):
        """Verify matching dark files are returned."""
        mock_ap_common.get_filtered_metadata.return_value = {
            "/path/dark1.fits": {},
            "/path/dark2.fits": {},
        }

        result = matching.find_matching_darks({}, ["/calibration"])

        assert len(result) == 2
        assert "/path/dark1.fits" in result


class TestFindMatchingFlats:
    """Tests for find_matching_flats function."""

    @patch("ap_move_lights_to_data.matching.ap_common")
    def test_includes_filter_in_match(self, mock_ap_common):
        """Verify filter is included in flat matching criteria."""
        mock_ap_common.get_filtered_metadata.return_value = {}

        light_metadata = {
            config.KEYWORD_CAMERA: "ASI2600MM",
            config.KEYWORD_FILTER: "Ha",
        }

        matching.find_matching_flats(light_metadata, ["/calibration"])

        call_args = mock_ap_common.get_filtered_metadata.call_args
        filters = call_args.kwargs["filters"]

        assert filters[config.KEYWORD_TYPE] == config.TYPE_FLAT
        assert filters[config.KEYWORD_FILTER] == "Ha"


class TestHasCalibrationFrames:
    """Tests for has_calibration_frames function."""

    @patch("ap_move_lights_to_data.matching.find_matching_flats")
    @patch("ap_move_lights_to_data.matching.find_matching_darks")
    def test_returns_true_when_both_exist(self, mock_darks, mock_flats):
        """Verify True returned when both darks and flats exist."""
        mock_darks.return_value = ["/dark1.fits", "/dark2.fits"]
        mock_flats.return_value = ["/flat1.fits"]

        has_darks, has_flats, dark_count, flat_count = matching.has_calibration_frames(
            {}, ["/cal"]
        )

        assert has_darks is True
        assert has_flats is True
        assert dark_count == 2
        assert flat_count == 1

    @patch("ap_move_lights_to_data.matching.find_matching_flats")
    @patch("ap_move_lights_to_data.matching.find_matching_darks")
    def test_returns_false_when_no_darks(self, mock_darks, mock_flats):
        """Verify False for darks when none exist."""
        mock_darks.return_value = []
        mock_flats.return_value = ["/flat1.fits"]

        has_darks, has_flats, _, _ = matching.has_calibration_frames({}, ["/cal"])

        assert has_darks is False
        assert has_flats is True

    @patch("ap_move_lights_to_data.matching.find_matching_flats")
    @patch("ap_move_lights_to_data.matching.find_matching_darks")
    def test_returns_false_when_no_flats(self, mock_darks, mock_flats):
        """Verify False for flats when none exist."""
        mock_darks.return_value = ["/dark1.fits"]
        mock_flats.return_value = []

        has_darks, has_flats, _, _ = matching.has_calibration_frames({}, ["/cal"])

        assert has_darks is True
        assert has_flats is False


class TestGetLightGroupMetadata:
    """Tests for get_light_group_metadata function."""

    @patch("ap_move_lights_to_data.matching.ap_common")
    def test_returns_none_when_no_files(self, mock_ap_common):
        """Verify None returned when no files found."""
        mock_ap_common.get_metadata.return_value = {}

        result = matching.get_light_group_metadata("/empty/dir")

        assert result is None

    @patch("ap_move_lights_to_data.matching.ap_common")
    def test_returns_first_light_metadata(self, mock_ap_common):
        """Verify first light's metadata is returned."""
        mock_ap_common.get_metadata.return_value = {
            "/path/light1.fits": {
                config.KEYWORD_TYPE: "light",
                config.KEYWORD_CAMERA: "ASI2600MM",
            },
            "/path/light2.fits": {
                config.KEYWORD_TYPE: "light",
                config.KEYWORD_CAMERA: "ASI2600MM",
            },
        }

        result = matching.get_light_group_metadata("/lights/dir")

        assert result is not None
        assert result[config.KEYWORD_TYPE] == "light"
