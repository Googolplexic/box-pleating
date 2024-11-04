"""Shared fixtures for box-pleating tests."""

import pytest
from box_pleating import BoxPleatingPattern, Point, CreaseType, Crease


@pytest.fixture
def empty_pattern():
    """Create an empty box-pleating pattern."""
    return BoxPleatingPattern(grid_size=10)


@pytest.fixture
def simple_pattern():
    """Create a simple pattern with basic mountain and valley folds."""
    pattern = BoxPleatingPattern(grid_size=10)
    pattern.add_crease(Point(0, 0), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(10, 5), CreaseType.VALLEY)
    return pattern


@pytest.fixture
def complex_pattern():
    """Create a more complex pattern for thorough testing."""
    pattern = BoxPleatingPattern(grid_size=10)

    # Create a simple box-pleating pattern
    # Base square
    pattern.add_crease(Point(2, 2), Point(8, 2), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(8, 2), Point(8, 8), CreaseType.VALLEY)
    pattern.add_crease(Point(8, 8), Point(2, 8), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(2, 8), Point(2, 2), CreaseType.VALLEY)

    # Diagonal folds
    pattern.add_crease(Point(2, 2), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(8, 2), Point(5, 5), CreaseType.VALLEY)
    pattern.add_crease(Point(8, 8), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(2, 8), Point(5, 5), CreaseType.VALLEY)

    return pattern


@pytest.fixture
def sample_fold_data():
    """Create sample FOLD format data."""
    return {
        "file_spec": 1.1,
        "file_creator": "test",
        "file_classes": ["creasePattern"],
        "frame_classes": ["creasePattern"],
        "vertices_coords": [[0.0, 0.0], [1.0, 1.0], [2.0, 1.0], [2.0, 0.0]],
        "edges_vertices": [[0, 1], [1, 2], [2, 3], [3, 0]],
        "edges_assignment": ["M", "V", "M", "V"],
        "edges_foldAngle": [-180, 180, -180, 180],
        "vertices_vertices": [[1, 3], [0, 2], [1, 3], [0, 2]],
    }


@pytest.fixture
def invalid_pattern():
    """Create an invalid pattern that violates folding rules."""
    pattern = BoxPleatingPattern(grid_size=10)

    # Create a pattern that violates Maekawa's theorem
    pattern.add_crease(Point(5, 5), Point(6, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(5, 6), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(4, 5), CreaseType.MOUNTAIN)

    return pattern


@pytest.fixture
def parallel_pattern():
    """Create a pattern with parallel creases for testing removal."""
    pattern = BoxPleatingPattern(grid_size=10)

    # Add parallel creases
    pattern.add_crease(Point(0, 5), Point(5, 5), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(5, 5), Point(10, 5), CreaseType.MOUNTAIN)

    return pattern


@pytest.fixture
def intersecting_pattern():
    """Create a pattern with intersecting creases."""
    pattern = BoxPleatingPattern(grid_size=10)

    # Add intersecting creases
    pattern.add_crease(Point(0, 0), Point(10, 10), CreaseType.MOUNTAIN)
    pattern.add_crease(Point(0, 10), Point(10, 0), CreaseType.VALLEY)

    return pattern
