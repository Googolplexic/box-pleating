"""Tests for grid-based operations."""

import pytest
import numpy as np
from box_pleating.grid_operations import (
    is_valid_crease,
    update_grid,
    is_corner_vertex,
    is_boundary_vertex,
    should_remove_vertex,
    merge_creases,
)
from box_pleating.models import Point, Crease, CreaseType



@pytest.fixture
def grid():
    """Create a test grid."""
    return np.zeros((11, 11), dtype=int)  # 10x10 grid (0-10 indices)


@pytest.fixture
def sample_points():
    """Create sample points for testing."""
    return {
        "origin": Point(0, 0),
        "middle": Point(5, 5),
        "corner": Point(10, 10),
        "edge": Point(0, 5),
        "diagonal": Point(3, 3),
    }


def test_is_valid_crease(sample_points):
    """Test crease validation."""
    grid_size = 10

    # Valid 45° crease
    assert is_valid_crease(
        sample_points["origin"], sample_points["diagonal"], grid_size
    )

    # Valid 90° crease
    assert is_valid_crease(sample_points["origin"], Point(0, 5), grid_size)

    # Invalid angle
    assert not is_valid_crease(sample_points["origin"], Point(3, 4), grid_size)

    # Out of bounds
    assert not is_valid_crease(sample_points["origin"], Point(11, 11), grid_size)

    # Zero length
    assert not is_valid_crease(
        sample_points["origin"], sample_points["origin"], grid_size
    )


def test_update_grid(grid, sample_points):
    """Test grid updating with creases."""
    update_grid(grid, sample_points["origin"], sample_points["diagonal"])

    # Check endpoints are marked
    assert grid[0, 0] == 1
    assert grid[3, 3] == 1

    # Check intermediate points are marked
    assert grid[1, 1] == 1
    assert grid[2, 2] == 1


def test_update_grid_bounds_checking(grid):
    """Test grid update with out-of-bounds coordinates."""
    update_grid(grid, Point(-1, -1), Point(15, 15))
    # Should not raise error but print warning

    # Check grid wasn't modified
    assert not np.any(grid)


def test_is_corner_vertex(sample_points):
    """Test corner vertex detection."""
    grid_size = 10

    # True for corners
    assert is_corner_vertex(Point(0, 0), grid_size)
    assert is_corner_vertex(Point(10, 10), grid_size)
    assert is_corner_vertex(Point(0, 10), grid_size)
    assert is_corner_vertex(Point(10, 0), grid_size)

    # False for non-corners
    assert not is_corner_vertex(sample_points["middle"], grid_size)
    assert not is_corner_vertex(sample_points["edge"], grid_size)


def test_is_boundary_vertex(sample_points):
    """Test boundary vertex detection."""
    grid_size = 10

    # True for boundaries
    assert is_boundary_vertex(sample_points["edge"], grid_size)
    assert is_boundary_vertex(Point(10, 5), grid_size)

    # False for internal points
    assert not is_boundary_vertex(sample_points["middle"], grid_size)
    assert not is_boundary_vertex(sample_points["diagonal"], grid_size)


def test_should_remove_vertex():
    """Test vertex removal conditions."""
    vertex = Point(5, 5)
    grid_size = 10

    # Parallel creases of same type
    parallel_creases = [
        Crease(Point(0, 5), vertex, CreaseType.MOUNTAIN),
        Crease(vertex, Point(10, 5), CreaseType.MOUNTAIN),
    ]
    assert should_remove_vertex(vertex, parallel_creases, grid_size)

    # Different crease types
    mixed_creases = [
        Crease(Point(0, 5), vertex, CreaseType.MOUNTAIN),
        Crease(vertex, Point(10, 5), CreaseType.VALLEY),
    ]
    assert not should_remove_vertex(vertex, mixed_creases, grid_size)

    # Non-parallel creases
    non_parallel_creases = [
        Crease(Point(0, 5), vertex, CreaseType.MOUNTAIN),
        Crease(vertex, Point(10, 10), CreaseType.MOUNTAIN),
    ]
    assert not should_remove_vertex(vertex, non_parallel_creases, grid_size)


def test_merge_creases():
    """Test crease merging."""
    vertex = Point(5, 5)
    crease1 = Crease(Point(0, 5), vertex, CreaseType.MOUNTAIN)
    crease2 = Crease(vertex, Point(10, 5), CreaseType.MOUNTAIN)

    merged = merge_creases(vertex, [crease1, crease2])
    assert merged is not None
    assert merged.start == Point(0, 5)
    assert merged.end == Point(10, 5)
    assert merged.type == CreaseType.MOUNTAIN


@pytest.mark.parametrize(
    "start,end,expected_valid",
    [
        (Point(0, 0), Point(5, 5), True),  # 45° angle
        (Point(0, 0), Point(5, 0), True),  # 90° angle
        (Point(0, 0), Point(3, 4), False),  # Invalid angle
        (Point(-1, 0), Point(5, 5), False),  # Out of bounds
        (Point(0, 0), Point(0, 0), False),  # Zero length
    ],
)
def test_parameterized_crease_validation(start, end, expected_valid):
    """Parameterized tests for crease validation."""
    assert is_valid_crease(start, end, grid_size=10) == expected_valid
