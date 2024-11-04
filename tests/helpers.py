"""Helper functions for testing box-pleating patterns."""

from typing import List, Tuple
import numpy as np
from box_pleating.models import Point, Crease, CreaseType


def assert_points_equal(p1: Point, p2: Point, epsilon: float = 1e-10) -> bool:
    """Assert that two points are equal within epsilon."""
    return abs(p1.x - p2.x) < epsilon and abs(p1.y - p2.y) < epsilon


def assert_creases_equal(c1: Crease, c2: Crease, epsilon: float = 1e-10) -> bool:
    """Assert that two creases are equal within epsilon."""
    return (
        assert_points_equal(c1.start, c2.start, epsilon)
        and assert_points_equal(c1.end, c2.end, epsilon)
        and c1.type == c2.type
    )


def create_grid_point_matrix(pattern_size: int) -> List[List[Point]]:
    """Create a matrix of grid points for testing."""
    return [
        [Point(x, y) for x in range(pattern_size + 1)] for y in range(pattern_size + 1)
    ]


def create_test_crease_pattern() -> List[Crease]:
    """Create a standard test crease pattern."""
    return [
        Crease(Point(0, 0), Point(2, 2), CreaseType.MOUNTAIN),
        Crease(Point(2, 2), Point(4, 2), CreaseType.VALLEY),
        Crease(Point(4, 2), Point(4, 0), CreaseType.MOUNTAIN),
        Crease(Point(4, 0), Point(0, 0), CreaseType.VALLEY),
    ]


def calculate_pattern_bounds(pattern) -> Tuple[float, float, float, float]:
    """Calculate the bounds of a pattern."""
    xs = [v.x for v in pattern.vertices]
    ys = [v.y for v in pattern.vertices]
    return min(xs), max(xs), min(ys), max(ys)


def count_crease_types(pattern) -> Tuple[int, int]:
    """Count mountain and valley creases in a pattern."""
    mountain_count = sum(1 for c in pattern.creases if c.type == CreaseType.MOUNTAIN)
    valley_count = sum(1 for c in pattern.creases if c.type == CreaseType.VALLEY)
    return mountain_count, valley_count


def verify_grid_consistency(pattern) -> bool:
    """Verify that the grid representation matches the creases."""
    if pattern.grid is None:
        return True

    # Create clean grid
    test_grid = np.zeros_like(pattern.grid)

    # Mark all vertices and crease points
    for vertex in pattern.vertices:
        x, y = vertex.grid_x, vertex.grid_y
        if 0 <= x < pattern.grid_size and 0 <= y < pattern.grid_size:
            test_grid[x, y] = 1

    # Compare grids
    return np.array_equal(test_grid, pattern.grid)


def assert_pattern_valid(pattern) -> List[str]:
    """
    Assert that a pattern is valid and return any violations.
    Returns empty list if valid, list of violation messages otherwise.
    """
    violations = []

    # Check grid bounds
    for vertex in pattern.vertices:
        if not (
            0 <= vertex.x <= pattern.grid_size and 0 <= vertex.y <= pattern.grid_size
        ):
            violations.append(f"Vertex {vertex} outside grid bounds")

    # Check crease angles
    for crease in pattern.creases:
        dx = crease.end.x - crease.start.x
        dy = crease.end.y - crease.start.y

        # Check for 45° or 90° angles
        if abs(dx) == abs(dy) or dx == 0 or dy == 0:
            continue
        violations.append(f"Crease {crease} not at valid angle")

    # Check for invalid intersections
    is_valid, report = pattern.is_valid_pattern()
    if not is_valid:
        if report["has_intersections"]:
            violations.append("Pattern has invalid intersections")
        if not report["is_flat_foldable"]:
            violations.append("Pattern not flat-foldable")

    return violations


def create_vertex_neighborhood(vertex: Point, radius: float = 1.0) -> List[Point]:
    """Create a list of points in the neighborhood of a vertex."""
    angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    return [
        Point(vertex.x + radius * np.cos(angle), vertex.y + radius * np.sin(angle))
        for angle in angles
    ]


def assert_kawasaki_satisfied(vertex: Point, creases: List[Crease]) -> bool:
    """Assert that Kawasaki's theorem is satisfied at a vertex."""
    if len(creases) < 4:
        return False

    # Calculate angles between consecutive creases
    vectors = []
    for crease in creases:
        if crease.start == vertex:
            vec = np.array([crease.end.x - vertex.x, crease.end.y - vertex.y])
        else:
            vec = np.array([crease.start.x - vertex.x, crease.start.y - vertex.y])
        vectors.append(vec)

    # Sort vectors by angle
    angles = []
    for i in range(len(vectors)):
        v1 = vectors[i]
        v2 = vectors[(i + 1) % len(vectors)]
        angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        angles.append(np.degrees(angle))

    # Check sum of alternate angles
    sum_even = sum(angles[::2])
    sum_odd = sum(angles[1::2])

    return abs(sum_even - sum_odd) < 1e-10
