import math
from typing import List, Tuple, Dict


def compute_minimum_spacing(vertices: List[List[float]]) -> float:
    """
    Compute the minimum non-zero spacing between vertices in the pattern.
    """
    if len(vertices) < 2:
        return 1.0

    min_spacing = float("inf")

    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            dx = abs(vertices[i][0] - vertices[j][0])
            dy = abs(vertices[i][1] - vertices[j][1])

            # Consider non-zero distances
            if dx > 0:
                min_spacing = min(min_spacing, dx)
            if dy > 0:
                min_spacing = min(min_spacing, dy)

    return min_spacing if min_spacing != float("inf") else 1.0


def compute_faces_vertices(
    vertices_coords: List[List[float]], edges_vertices: List[List[int]]
) -> List[List[int]]:
    """
    Compute faces from edges following FOLD spec approach.
    Returns list of vertex indices for each face in counterclockwise order.
    """
    # Create vertices_vertices (adjacency list)
    num_vertices = len(vertices_coords)
    vertices_vertices = [[] for _ in range(num_vertices)]
    for v1, v2 in edges_vertices:
        vertices_vertices[v1].append(v2)
        vertices_vertices[v2].append(v1)

    # Sort vertices around each vertex counterclockwise
    for v, neighbors in enumerate(vertices_vertices):
        if not neighbors:
            continue
        # Calculate angles for sorting
        angles = []
        for n in neighbors:
            dx = vertices_coords[n][0] - vertices_coords[v][0]
            dy = vertices_coords[n][1] - vertices_coords[v][1]
            angle = math.atan2(dy, dx)
            angles.append((angle, n))
        # Sort neighbors counterclockwise
        sorted_pairs = sorted(angles)
        vertices_vertices[v] = [n for _, n in sorted_pairs]

    # Build next mapping from sorted neighbors
    next_map = {}
    for v, neighbors in enumerate(vertices_vertices):
        for i, n in enumerate(neighbors):
            prev = neighbors[(i - 1) % len(neighbors)]
            next_map[(v, n)] = prev

    # Find faces
    faces = []
    for start_edge in edges_vertices:
        # Try both directions of each edge
        for v1, v2 in [(start_edge[0], start_edge[1]), (start_edge[1], start_edge[0])]:
            face = [v1, v2]
            while True:
                if len(face) > len(edges_vertices):
                    break

                curr = face[-1]
                prev = face[-2]
                next_v = next_map.get((curr, prev))

                if next_v is None:
                    break

                if next_v == face[0]:
                    # Check if this forms a valid CCW face
                    area = 0
                    for i in range(len(face)):
                        j = (i + 1) % len(face)
                        vi = vertices_coords[face[i]]
                        vj = vertices_coords[face[j]]
                        area += vi[0] * vj[1] - vj[0] * vi[1]

                    if area > 0 and len(face) >= 3:
                        # Check if this is a new face (not just a cyclic rotation)
                        face_set = frozenset(face)
                        if not any(
                            frozenset(existing) == face_set for existing in faces
                        ):
                            faces.append(face[:])
                    break

                if next_v in face[:-1]:
                    break

                face.append(next_v)

    return faces


def compute_scale_factors(
    coords: List[List[float]],
) -> Tuple[float, float, float, float, float]:
    """
    Compute scale factors and offsets for coordinate conversion.
    Returns (scale_factor, min_x, min_y, center_x, center_y)
    """
    if not coords:
        return 1.0, 0.0, 0.0, 0.0, 0.0

    # Extract x and y coordinates
    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]

    # Calculate bounds
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Calculate centers
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Calculate scale factor based on the larger dimension
    width = max_x - min_x
    height = max_y - min_y

    # Prevent division by zero
    if width == 0 and height == 0:
        scale_factor = 1.0
    else:
        # Use the larger dimension to determine scale
        max_dimension = max(width, height)
        scale_factor = 400 / max_dimension if max_dimension != 0 else 1.0

    return scale_factor, min_x, min_y, center_x, center_y
