"""Tests for the FOLD format converter."""

import pytest
import json
from box_pleating.fold import FoldConverter
from box_pleating import BoxPleatingPattern, Point, CreaseType


@pytest.fixture
def converter():
    """Create a converter instance for testing."""
    return FoldConverter()


@pytest.fixture
def sample_fold_data():
    """Create sample FOLD format data for testing."""
    return {
        "file_spec": 1.1,
        "file_creator": "test",
        "file_classes": ["creasePattern"],
        "frame_classes": ["creasePattern"],
        "vertices_coords": [[0.0, 0.0], [1.0, 1.0], [2.0, 1.0]],
        "edges_vertices": [[0, 1], [1, 2]],
        "edges_assignment": ["M", "V"],
        "edges_foldAngle": [-180, 180],
    }


@pytest.fixture
def sample_pattern():
    """Create a sample box-pleating pattern for testing."""
    pattern = BoxPleatingPattern(grid_size=10)
    pattern.add_crease(Point(0, 0), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(10, 5), CreaseType.VALLEY)
    return pattern


def test_fold_to_pattern_conversion(converter, sample_fold_data):
    """Test converting FOLD data to BoxPleatingPattern."""
    pattern = converter.from_fold(sample_fold_data)
    assert isinstance(pattern, BoxPleatingPattern)
    assert len(pattern.vertices) > 0
    assert len(pattern.creases) > 0


def test_pattern_to_fold_conversion(converter, sample_pattern):
    """Test converting BoxPleatingPattern to FOLD format."""
    fold_data = converter.to_fold(sample_pattern)
    assert isinstance(fold_data, dict)
    assert "vertices_coords" in fold_data
    assert "edges_vertices" in fold_data
    assert "edges_assignment" in fold_data
    assert len(fold_data["vertices_coords"]) > 0
    assert len(fold_data["edges_vertices"]) > 0


def test_roundtrip_conversion(converter, sample_pattern):
    """Test converting pattern to FOLD and back preserves structure."""
    fold_data = converter.to_fold(sample_pattern)
    new_pattern = converter.from_fold(fold_data)

    assert len(new_pattern.vertices) == len(sample_pattern.vertices)
    assert len(new_pattern.creases) == len(sample_pattern.creases)


def test_invalid_fold_data(converter):
    """Test handling of invalid FOLD data."""
    invalid_data = {"file_spec": 1.1, "vertices_coords": []}  # Empty vertices

    pattern = converter.from_fold(invalid_data)
    assert isinstance(pattern, BoxPleatingPattern)
    assert len(pattern.vertices) == 0


@pytest.mark.parametrize(
    "file_content,expected_error",
    [
        ("{invalid_json}", json.JSONDecodeError),
        ("", FileNotFoundError),
    ],
)
def test_load_fold_file_errors(converter, tmp_path, file_content, expected_error):
    """Test error handling when loading FOLD files."""
    test_file = tmp_path / "test.fold"

    if file_content:
        test_file.write_text(file_content)

    with pytest.raises(expected_error):
        converter.load_fold(str(test_file))
