import numpy as np
from typing import List, Optional
from .models import Point, Crease
import logging

logger = logging.getLogger(__name__)

def is_valid_crease(start: Point, end: Point, grid_size: int, epsilon: float = 1e-10) -> bool:
    """
    Check if a proposed crease follows box-pleating rules.
    
    Box pleating rules:
    - Points must be different
    - Points must be within grid bounds
    - Points must be at integer coordinates
    - Lines must be at 45° or 90° angles
    """
    # Check that start and end points are different
    if (abs(start.x - end.x) < epsilon and abs(start.y - end.y) < epsilon):
        logger.debug(
            "Invalid crease: Start point (%f, %f) equals end point (%f, %f)",
            start.x,
            start.y,
            end.x,
            end.y,
        )
        return False

    # Check if points are within grid bounds
    if not (0 <= start.x <= grid_size and 
            0 <= start.y <= grid_size and 
            0 <= end.x <= grid_size and 
            0 <= end.y <= grid_size):
        logger.debug(f"Invalid crease: Points out of grid bounds")
        return False

    # Check for integer coordinates
    if (abs(round(start.x) - start.x) > epsilon or 
        abs(round(start.y) - start.y) > epsilon or 
        abs(round(end.x) - end.x) > epsilon or 
        abs(round(end.y) - end.y) > epsilon):
        logger.debug(f"Invalid crease: Points not at integer coordinates")
        return False

    # Calculate differences and check angles
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    # Check for zero length
    length = (dx * dx + dy * dy) ** 0.5
    if length < epsilon:
        logger.debug(f"Invalid crease: Zero length")
        return False

    # Check for 45° or 90° angles
    if abs(dx - dy) < epsilon:  # 45° angle
        return abs(round(dx) - dx) < epsilon
    elif dx < epsilon:  # Vertical line
        return abs(round(dy) - dy) < epsilon
    elif dy < epsilon:  # Horizontal line
        return abs(round(dx) - dx) < epsilon

    logger.debug(f"Invalid crease: Not a 45° or 90° angle")
    return False

def update_grid(grid: np.ndarray, start: Point, end: Point) -> None:
    """Update the grid with a new crease."""
    if grid is None:
        return

    # Convert coordinates to integers for grid indexing
    start_x = start.grid_x
    start_y = start.grid_y
    end_x = end.grid_x
    end_y = end.grid_y

    # Check bounds
    grid_size = grid.shape[0] - 1
    if not (0 <= start_x <= grid_size and 
            0 <= start_y <= grid_size and 
            0 <= end_x <= grid_size and 
            0 <= end_y <= grid_size):
        logger.warning(
            f"Warning: Attempted to update grid with out-of-bounds coordinates: "
            f"({start_x}, {start_y}) -> ({end_x}, {end_y})"
        )
        return

    # Mark endpoints
    grid[start_x, start_y] = 1
    grid[end_x, end_y] = 1

    # Mark intermediate points along the crease
    dx = end_x - start_x
    dy = end_y - start_y
    steps = max(abs(dx), abs(dy))
    if steps > 0:
        for i in range(steps + 1):
            x = round(start_x + (dx * i) / steps)
            y = round(start_y + (dy * i) / steps)
            if 0 <= x <= grid_size and 0 <= y <= grid_size:
                grid[x, y] = 1

def is_corner_vertex(vertex: Point, grid_size: int) -> bool:
    """Check if a vertex is at the corner of the pattern."""
    return ((vertex.x == 0 and vertex.y == 0) or
            (vertex.x == 0 and vertex.y == grid_size) or
            (vertex.x == grid_size and vertex.y == 0) or
            (vertex.x == grid_size and vertex.y == grid_size))

def is_boundary_vertex(vertex: Point, grid_size: int) -> bool:
    """Check if a vertex is on the boundary of the pattern."""
    return (vertex.x == 0 or
            vertex.x == grid_size or
            vertex.y == 0 or
            vertex.y == grid_size)

def should_remove_vertex(vertex: Point, connected_creases: List[Crease], grid_size: int) -> bool:
    """Determine if a vertex should be removed based on box-pleating rules."""
    from .geometry import are_edges_parallel
    
    # Only consider vertices with exactly two creases
    if len(connected_creases) != 2:
        return False

    # Don't remove corner vertices
    if is_corner_vertex(vertex, grid_size):
        return False

    crease1, crease2 = connected_creases

    # Creases must be of same type
    if crease1.type != crease2.type:
        return False

    # Creases must be parallel
    return are_edges_parallel(crease1, crease2)

def merge_creases(vertex: Point, creases_to_merge: List[Crease]) -> Optional[Crease]:
    """Merge two creases that meet at a vertex into a single crease."""
    if len(creases_to_merge) != 2:
        return None

    crease1, crease2 = creases_to_merge

    # Find the endpoints that aren't the common vertex
    if crease1.start == vertex:
        start = crease1.end
    else:
        start = crease1.start

    if crease2.start == vertex:
        end = crease2.end
    else:
        end = crease2.start

    # Create new merged crease
    return Crease(start, end, crease1.type)
