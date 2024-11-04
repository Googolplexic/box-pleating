"""Tests for the core data models."""

import pytest
from box_pleating.models import Point, Crease, CreaseType


def test_point_creation():
    """Test Point creation and properties."""
    point = Point(1.0, 2.0)
    assert point.x == 1.0
    assert point.y == 2.0
    assert point.grid_x == 1
    assert point.grid_y == 2


def test_point_equality():
    """Test Point equality comparison."""
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    p3 = Point(1.0, 3.0)

    assert p1 == p2
    assert p1 != p3
    assert hash(p1) == hash(p2)


def test_point_from_list():
    """Test Point creation from list."""
    coords = [1.0, 2.0]
    point = Point.from_list(coords)
    assert point.x == 1.0
    assert point.y == 2.0


def test_point_to_list():
    """Test Point conversion to list."""
    point = Point(1.0, 2.0)
    coords = point.to_list()
    assert coords == [1.0, 2.0]


def test_crease_creation():
    """Test Crease creation and properties."""
    start = Point(0.0, 0.0)
    end = Point(1.0, 1.0)
    crease = Crease(start, end, CreaseType.MOUNTAIN)

    assert crease.start == start
    assert crease.end == end
    assert crease.type == CreaseType.MOUNTAIN


def test_crease_type_values():
    """Test CreaseType enum values."""
    assert CreaseType.NONE.value == 0
    assert CreaseType.MOUNTAIN.value == 1
    assert CreaseType.VALLEY.value == -1
    assert CreaseType.BORDER.value == 2
