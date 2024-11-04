import numpy as np
from typing import List, Tuple, Dict
from .models import Point, Crease, CreaseType


def sort_vectors_counterclockwise(
    vertex: Point, vertex_creases: List[Crease]
) -> List[Tuple[np.ndarray, Crease]]:
    """Sort vectors around a vertex in counterclockwise order."""
    vectors_and_creases = []
    for crease in vertex_creases:
        if crease.start == vertex:
            vec = np.array([crease.end.x - vertex.x, crease.end.y - vertex.y])
        else:
            vec = np.array([crease.start.x - vertex.x, crease.start.y - vertex.y])
        vectors_and_creases.append((vec, crease))

    # Sort by angle with respect to positive x-axis
    angles = [np.arctan2(v[1], v[0]) for v, _ in vectors_and_creases]
    sorted_pairs = sorted(zip(angles, vectors_and_creases))
    return [vc for _, vc in sorted_pairs]


def calculate_angles(vertex: Point, vertex_creases: List[Crease]) -> List[float]:
    """Calculate angles between creases at a vertex in cyclic order."""
    if len(vertex_creases) < 2:
        return []

    # Convert creases to vectors and sort them cyclically
    vectors_and_creases = []
    for crease in vertex_creases:
        if crease.start == vertex:
            vec = np.array([crease.end.x - vertex.x, crease.end.y - vertex.y])
        else:
            vec = np.array([crease.start.x - vertex.x, crease.start.y - vertex.y])
        vectors_and_creases.append((vec, crease))

    # Sort vectors by angle
    angles_and_pairs = []
    for vec, crease in vectors_and_creases:
        angle = np.arctan2(vec[1], vec[0])
        if angle < 0:
            angle += 2 * np.pi
        angles_and_pairs.append((angle, (vec, crease)))

    sorted_pairs = sorted(angles_and_pairs, key=lambda x: x[0])
    sorted_vectors = [pair[1][0] for pair in sorted_pairs]

    # Calculate consecutive angles
    angles = []
    for i in range(len(sorted_vectors)):
        v1 = sorted_vectors[i]
        v2 = sorted_vectors[(i + 1) % len(sorted_vectors)]

        dot_product = np.dot(v1, v2)
        norms_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_theta = np.clip(dot_product / norms_product, -1.0, 1.0)
        angle = np.arccos(cos_theta)
        angles.append(np.degrees(angle))

    return angles


def check_kawasaki_theorem(
    vertex: Point, vertex_creases: List[Crease], grid_size: int
) -> Tuple[bool, Dict]:
    """Check if Kawasaki's theorem is satisfied at a vertex."""
    # Edge vertices are always valid
    if vertex.x == 0 or vertex.y == 0 or vertex.x == grid_size or vertex.y == grid_size:
        return True, {
            "is_edge_vertex": True,
            "angle_count": 0,
            "angle_difference": 0,
        }

    if len(vertex_creases) < 4:  # Need at least 4 creases for internal vertex
        return False, {
            "is_edge_vertex": False,
            "angle_count": len(vertex_creases),
            "error": "Insufficient creases",
            "min_required": 4,
        }

    angles = calculate_angles(vertex, vertex_creases)

    # Calculate alternating sums
    sum_odd = sum(angles[1::2])
    sum_even = sum(angles[::2])
    angle_difference = abs(sum_odd - sum_even)

    # Allow for small numerical imprecision (0.1 degrees)
    is_satisfied = angle_difference < 0.1

    return is_satisfied, {
        "is_edge_vertex": False,
        "angle_count": len(angles),
        "angles": angles,
        "sum_odd": sum_odd,
        "sum_even": sum_even,
        "angle_difference": angle_difference,
    }


def check_maekawa_theorem(
    vertex: Point, vertex_creases: List[Crease], grid_size: int
) -> Tuple[bool, Dict]:
    """Check if Maekawa's theorem is satisfied at a vertex."""
    # Edge vertices are always valid
    if vertex.x == 0 or vertex.y == 0 or vertex.x == grid_size or vertex.y == grid_size:
        return True, {
            "is_edge_vertex": True,
            "mountain_count": 0,
            "valley_count": 0,
            "difference": 0,
        }

    mountain_count = sum(1 for c in vertex_creases if c.type == CreaseType.MOUNTAIN)
    valley_count = sum(1 for c in vertex_creases if c.type == CreaseType.VALLEY)

    difference = abs(mountain_count - valley_count)
    is_satisfied = difference == 2

    return is_satisfied, {
        "is_edge_vertex": False,
        "mountain_count": mountain_count,
        "valley_count": valley_count,
        "difference": difference,
        "connected_creases": len(vertex_creases),
    }
