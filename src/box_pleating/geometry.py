import numpy as np
from typing import Optional
from .models import Point, Crease


def segments_intersect(
    p1: Point, p2: Point, p3: Point, p4: Point, epsilon: float = 1e-10
) -> bool:
    """
    Check if line segment p1p2 intersects with line segment p3p4.
    Handles all cases including overlapping lines.
    """
    # First check for complete overlap
    if (
        abs(p1.x - p3.x) < epsilon
        and abs(p1.y - p3.y) < epsilon
        and abs(p2.x - p4.x) < epsilon
        and abs(p2.y - p4.y) < epsilon
    ) or (
        abs(p1.x - p4.x) < epsilon
        and abs(p1.y - p4.y) < epsilon
        and abs(p2.x - p3.x) < epsilon
        and abs(p2.y - p3.y) < epsilon
    ):
        return True

    # Check if segments share an endpoint (this is allowed)
    if (
        (abs(p1.x - p3.x) < epsilon and abs(p1.y - p3.y) < epsilon)
        or (abs(p1.x - p4.x) < epsilon and abs(p1.y - p4.y) < epsilon)
        or (abs(p2.x - p3.x) < epsilon and abs(p2.y - p3.y) < epsilon)
        or (abs(p2.x - p4.x) < epsilon and abs(p2.y - p4.y) < epsilon)
    ):
        return False

    def on_segment(p: Point, q: Point, r: Point) -> bool:
        """Check if point q lies on segment pr"""
        if (
            q.x <= max(p.x, r.x) + epsilon
            and q.x >= min(p.x, r.x) - epsilon
            and q.y <= max(p.y, r.y) + epsilon
            and q.y >= min(p.y, r.y) - epsilon
        ):
            numerator = abs(
                (r.y - p.y) * q.x - (r.x - p.x) * q.y + r.x * p.y - r.y * p.x
            )
            denominator = ((r.y - p.y) ** 2 + (r.x - p.x) ** 2) ** 0.5
            if denominator < epsilon:
                return True
            distance = numerator / denominator
            return distance < epsilon
        return False

    def collinear(p1: Point, p2: Point, p3: Point) -> bool:
        """Check if three points are collinear using area of triangle"""
        area = abs(
            (p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)) / 2.0
        )
        return area < epsilon

    # Check if all points are collinear
    if collinear(p1, p2, p3) and collinear(p1, p2, p4):
        # Check for any overlap
        if (
            on_segment(p1, p3, p2)
            or on_segment(p1, p4, p2)
            or on_segment(p3, p1, p4)
            or on_segment(p3, p2, p4)
        ):
            return True
        return False

    def direction(p1: Point, p2: Point, p3: Point) -> float:
        """Calculate direction of turn from p1->p2->p3"""
        return (p3.x - p1.x) * (p2.y - p1.y) - (p2.x - p1.x) * (p3.y - p1.y)

    # Not collinear - check for regular intersection
    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4)

    return ((d1 > epsilon and d2 < -epsilon) or (d1 < -epsilon and d2 > epsilon)) and (
        (d3 > epsilon and d4 < -epsilon) or (d3 < -epsilon and d4 > epsilon)
    )


def find_intersection_point(
    p1: Point, p2: Point, p3: Point, p4: Point, epsilon: float = 1e-10
) -> Optional[Point]:
    """
    Find the intersection point of two line segments if it exists.
    Returns None if segments are parallel or don't intersect.
    """
    # Convert to numpy arrays for easier calculation
    p1_arr = np.array([p1.x, p1.y])
    p2_arr = np.array([p2.x, p2.y])
    p3_arr = np.array([p3.x, p3.y])
    p4_arr = np.array([p4.x, p4.y])

    # Line segment vectors
    v1 = p2_arr - p1_arr
    v2 = p4_arr - p3_arr

    # Cross product to check for parallel lines
    cross = np.cross(v1, v2)
    if abs(cross) < epsilon:  # Lines are parallel
        return None

    # Calculate intersection using parametric form
    x = p3_arr - p1_arr
    A = np.array([v1, -v2]).T
    try:
        t, s = np.linalg.solve(A, x)
        if 0 <= t <= 1 and 0 <= s <= 1:  # Check if intersection is within segments
            intersection = p1_arr + t * v1
            return Point(float(intersection[0]), float(intersection[1]))
    except np.linalg.LinAlgError:
        return None
    return None


def segments_overlap(
    p1: Point, p2: Point, p3: Point, p4: Point, epsilon: float = 1e-10
) -> bool:
    """Check if two line segments overlap (excluding shared endpoints)."""

    # For vertical lines
    if abs(p2.x - p1.x) < epsilon and abs(p4.x - p3.x) < epsilon:
        if abs(p1.x - p3.x) >= epsilon:
            return False
        y_min1, y_max1 = min(p1.y, p2.y), max(p1.y, p2.y)
        y_min2, y_max2 = min(p3.y, p4.y), max(p3.y, p4.y)
        return y_min1 < y_max2 and y_max1 > y_min2

    # For horizontal lines
    if abs(p2.y - p1.y) < epsilon and abs(p4.y - p3.y) < epsilon:
        if abs(p1.y - p3.y) >= epsilon:
            return False
        x_min1, x_max1 = min(p1.x, p2.x), max(p1.x, p2.x)
        x_min2, x_max2 = min(p3.x, p4.x), max(p3.x, p4.x)
        return x_min1 < x_max2 and x_max1 > x_min2

    # For diagonal lines
    dx1, dy1 = p2.x - p1.x, p2.y - p1.y
    dx2, dy2 = p4.x - p3.x, p4.y - p3.y

    if abs(dx1) < epsilon or abs(dx2) < epsilon:
        return False  # Should have been caught by vertical line check

    slope1 = dy1 / dx1
    slope2 = dy2 / dx2

    if abs(slope1 - slope2) >= epsilon:
        return False

    # Calculate y-intercepts
    b1 = p1.y - slope1 * p1.x
    b2 = p3.y - slope2 * p3.x

    if abs(b1 - b2) >= epsilon:
        return False

    x_min1, x_max1 = min(p1.x, p2.x), max(p1.x, p2.x)
    x_min2, x_max2 = min(p3.x, p4.x), max(p3.x, p4.x)

    return x_min1 < x_max2 and x_max1 > x_min2


def calculate_vector_angle(vec: np.ndarray) -> float:
    """Calculate the angle of a vector relative to positive x-axis."""
    return np.arctan2(vec[1], vec[0])


def point_on_crease(point: Point, crease: Crease, epsilon: float = 1e-10) -> bool:
    """Check if a point lies on a crease segment."""
    # Check bounding box
    if not (
        min(crease.start.x, crease.end.x) - epsilon
        <= point.x
        <= max(crease.start.x, crease.end.x) + epsilon
        and min(crease.start.y, crease.end.y) - epsilon
        <= point.y
        <= max(crease.start.y, crease.end.y) + epsilon
    ):
        return False

    # For vertical lines
    if abs(crease.end.x - crease.start.x) < epsilon:
        return abs(point.x - crease.start.x) < epsilon

    # For other lines, check using slope
    slope = (crease.end.y - crease.start.y) / (crease.end.x - crease.start.x)
    expected_y = crease.start.y + slope * (point.x - crease.start.x)
    return abs(point.y - expected_y) < epsilon


def are_edges_parallel(edge1: Crease, edge2: Crease, epsilon: float = 1e-6) -> bool:
    """Check if two edges/creases are parallel within a given epsilon."""
    vec1 = np.array([edge1.end.x - edge1.start.x, edge1.end.y - edge1.start.y])
    vec2 = np.array([edge2.end.x - edge2.start.x, edge2.end.y - edge2.start.y])

    vec1_norm = np.linalg.norm(vec1)
    vec2_norm = np.linalg.norm(vec2)

    if vec1_norm < epsilon or vec2_norm < epsilon:
        return False

    vec1 = vec1 / vec1_norm
    vec2 = vec2 / vec2_norm

    cross_product = abs(np.cross(vec1, vec2))
    return cross_product < epsilon
