"""Tests for the BoxPleatingPattern class."""

import pytest
from box_pleating import BoxPleatingPattern, Point, CreaseType


@pytest.fixture
def empty_pattern():
    """Create an empty pattern for testing."""
    return BoxPleatingPattern(grid_size=10)


@pytest.fixture
def simple_pattern():
    """Create a pattern with some basic creases."""
    pattern = BoxPleatingPattern(grid_size=10)
    pattern.add_crease(Point(0, 0), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(10, 5), CreaseType.VALLEY)
    return pattern


def test_pattern_creation(empty_pattern):
    """Test pattern initialization."""
    assert empty_pattern.grid_size == 10
    assert empty_pattern.grid is not None
    assert len(empty_pattern.vertices) == 0
    assert len(empty_pattern.creases) == 0


def test_add_valid_crease(empty_pattern):
    """Test adding a valid crease."""
    result = empty_pattern.add_crease(Point(0, 0), Point(5, 5), CreaseType.MOUNTAIN)
    assert result is True
    assert len(empty_pattern.creases) == 1
    assert len(empty_pattern.vertices) == 2


def test_add_invalid_crease(empty_pattern):
    """Test adding an invalid crease (not 45° or 90°)."""
    result = empty_pattern.add_crease(Point(0, 0), Point(3, 4), CreaseType.MOUNTAIN)
    assert result is False
    assert len(empty_pattern.creases) == 0


def test_is_flat_foldable(simple_pattern):
    """Test flat-foldability check."""
    is_foldable, violations = simple_pattern.is_flat_foldable()
    assert isinstance(is_foldable, bool)
    assert isinstance(violations, list)


def test_remove_redundant_vertices(empty_pattern):
    """Test redundant vertex removal."""
    # Add two collinear creases
    empty_pattern.add_crease(Point(0, 0), Point(5, 0), CreaseType.MOUNTAIN)
    empty_pattern.add_crease(Point(5, 0), Point(10, 0), CreaseType.MOUNTAIN)

    initial_vertex_count = len(empty_pattern.vertices)
    empty_pattern.remove_redundant_vertices()
    final_vertex_count = len(empty_pattern.vertices)

    assert final_vertex_count < initial_vertex_count


def test_pattern_validation(simple_pattern):
    """Test overall pattern validation."""
    is_valid, report = simple_pattern.is_valid_pattern()
    assert isinstance(is_valid, bool)
    assert isinstance(report, dict)
    assert "is_flat_foldable" in report
    assert "foldability_violations" in report
    assert "has_intersections" in report
