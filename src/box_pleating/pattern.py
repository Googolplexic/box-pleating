import json
import numpy as np
from typing import Dict, List, Tuple
from .models import Point, Crease, CreaseType
from .geometry import (
    segments_intersect,
    find_intersection_point,
    segments_overlap,
    point_on_crease,
)
from .grid_operations import (
    is_valid_crease,
    update_grid,
    should_remove_vertex,
    merge_creases,
    is_boundary_vertex,
)
from .theorems import check_kawasaki_theorem, check_maekawa_theorem
import logging

logger = logging.getLogger(__name__)


class BoxPleatingPattern:
    """
    A class representing a box-pleating origami pattern.

    Box pleating is a tessellation technique in origami where all creases are at
    45° or 90° angles to each other, forming a grid-like pattern.
    """

    def __init__(self, grid_size: int = None):
        """Initialize a box-pleating pattern with optional grid size."""
        self.grid_size = grid_size
        self.vertices: List[Point] = []
        self.creases: List[Crease] = []
        self.grid = None
        if grid_size is not None:
            self.grid = np.zeros((grid_size + 1, grid_size + 1), dtype=int)

    def __str__(self):
        """Return a string representation of the pattern."""
        pattern_data = {
            "grid_size": self.grid_size,
            "creases": [
                {
                    "start": {"x": crease.start.x, "y": crease.start.y},
                    "end": {"x": crease.end.x, "y": crease.end.y},
                    "type": crease.type.name,
                }
                for crease in self.creases
            ],
            "vertices": [{"x": vertex.x, "y": vertex.y} for vertex in self.vertices],
        }
        return json.dumps(pattern_data, indent=2)

    def add_crease(
        self, start: Point, end: Point, crease_type: CreaseType, force: bool = False
    ) -> bool:
        """Add a crease between two points, splitting it at intersections if necessary."""
        if not is_valid_crease(start, end, self.grid_size):
            return False

        # Create temporary crease for checking
        new_crease = Crease(start, end, crease_type)

        # If force is True, add the crease without checking intersections
        if force:
            self.creases.append(new_crease)
            if start not in self.vertices:
                self.vertices.append(start)
            if end not in self.vertices:
                self.vertices.append(end)
            if self.grid is not None:
                update_grid(self.grid, start, end)
            return True

        # Check for overlapping parallel segments
        for existing_crease in self.creases:
            if segments_overlap(start, end, existing_crease.start, existing_crease.end):
                logger.debug(
                    f"Overlapping parallel segments detected between "
                    f"({start.x}, {start.y})->({end.x}, {end.y}) and "
                    f"({existing_crease.start.x}, {existing_crease.start.y})->"
                    f"({existing_crease.end.x}, {existing_crease.end.y})"
                )
                return False

        # Find all intersections with existing creases
        intersections = self._find_all_intersections(start, end)

        # If no intersections, add the crease normally
        if not intersections:
            self.creases.append(new_crease)
            if start not in self.vertices:
                self.vertices.append(start)
            if end not in self.vertices:
                self.vertices.append(end)
            if self.grid is not None:
                update_grid(self.grid, start, end)
            return True

        # Process intersections and add new vertices/creases
        self._process_intersections(start, end, crease_type, intersections)
        return True

    def _find_all_intersections(self, start: Point, end: Point) -> List[Point]:
        """Find all intersection points between a proposed new crease and existing creases."""
        intersections = []
        for existing_crease in self.creases:
            # Skip if creases share an endpoint
            if (
                start == existing_crease.start
                or start == existing_crease.end
                or end == existing_crease.start
                or end == existing_crease.end
            ):
                continue

            intersection = find_intersection_point(
                start, end, existing_crease.start, existing_crease.end
            )
            if intersection:
                intersections.append(intersection)

        # Sort intersections by distance from start point
        if intersections:
            start_arr = np.array([start.x, start.y])
            intersections.sort(
                key=lambda p: np.linalg.norm(np.array([p.x, p.y]) - start_arr)
            )

        return intersections

    def _process_intersections(
        self,
        start: Point,
        end: Point,
        crease_type: CreaseType,
        intersections: List[Point],
    ) -> None:
        """Process intersections and add new vertices and creases."""
        # Add start point if it's not already a vertex
        if start not in self.vertices:
            self.vertices.append(start)

        # Add all intersection points as vertices
        for point in intersections:
            if point not in self.vertices:
                self.vertices.append(point)

        # Add end point if it's not already a vertex
        if end not in self.vertices:
            self.vertices.append(end)

        # Create creases between consecutive points
        points = [start] + intersections + [end]
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            self.creases.append(Crease(p1, p2, crease_type))
            if self.grid is not None:
                update_grid(self.grid, p1, p2)

        # Split existing creases at intersections
        self._split_intersecting_creases(intersections)

    def _split_intersecting_creases(self, intersections: List[Point]) -> None:
        """Split existing creases that intersect with the new segments."""
        creases_to_remove = []
        creases_to_add = []

        for existing_crease in self.creases:
            intersecting_points = [
                p for p in intersections if point_on_crease(p, existing_crease)
            ]

            if intersecting_points:
                creases_to_remove.append(existing_crease)
                # Split the existing crease at all intersection points
                current_segments = [existing_crease]
                for point in intersecting_points:
                    new_segments = []
                    for segment in current_segments:
                        new_segments.extend(self._split_crease_at_point(segment, point))
                    current_segments = new_segments
                creases_to_add.extend(current_segments)

        # Remove old creases and add new ones
        self.creases = [c for c in self.creases if c not in creases_to_remove]
        self.creases.extend(creases_to_add)

    def _split_crease_at_point(self, crease: Crease, point: Point) -> List[Crease]:
        """Split a crease into two creases at the given point."""
        if point == crease.start or point == crease.end:
            return [crease]

        return [
            Crease(crease.start, point, crease.type),
            Crease(point, crease.end, crease.type),
        ]

    def check_crease_intersections(self) -> List[Dict]:
        """Check for all intersecting creases in the pattern."""
        intersections = []

        for i, crease1 in enumerate(self.creases):
            for j, crease2 in enumerate(self.creases[i + 1 :], i + 1):
                # Skip if creases share an endpoint
                if (
                    crease1.start == crease2.start
                    or crease1.start == crease2.end
                    or crease1.end == crease2.start
                    or crease1.end == crease2.end
                ):
                    continue

                if segments_intersect(
                    crease1.start, crease1.end, crease2.start, crease2.end
                ):
                    # Calculate intersection point
                    t = 0.5  # This works for box-pleating grid intersections
                    dx1 = crease1.end.x - crease1.start.x
                    dy1 = crease1.end.y - crease1.start.y
                    x = crease1.start.x + t * dx1
                    y = crease1.start.y + t * dy1

                    intersection = {
                        "crease1": {
                            "start": {"x": crease1.start.x, "y": crease1.start.y},
                            "end": {"x": crease1.end.x, "y": crease1.end.y},
                            "type": crease1.type.name,
                        },
                        "crease2": {
                            "start": {"x": crease2.start.x, "y": crease2.start.y},
                            "end": {"x": crease2.end.x, "y": crease2.end.y},
                            "type": crease2.type.name,
                        },
                        "intersection_point": {"x": x, "y": y},
                    }
                    intersections.append(intersection)

        return intersections

    def get_connected_creases(self, vertex: Point) -> List[Crease]:
        """Get all creases connected to a vertex."""
        return [
            crease
            for crease in self.creases
            if crease.start == vertex or crease.end == vertex
        ]

    def is_flat_foldable(self) -> Tuple[bool, List[Dict]]:
        """
        Check if the entire pattern is flat-foldable by verifying Kawasaki's and
        Maekawa's theorems at each vertex.
        """
        is_foldable = True
        violations = []

        for vertex in self.vertices:
            vertex_creases = self.get_connected_creases(vertex)
            maekawa_valid, maekawa_details = check_maekawa_theorem(
                vertex, vertex_creases, self.grid_size
            )
            kawasaki_valid, kawasaki_details = check_kawasaki_theorem(
                vertex, vertex_creases, self.grid_size
            )

            if not (maekawa_valid and kawasaki_valid):
                is_foldable = False
                violation = {
                    "vertex": {"x": vertex.x, "y": vertex.y},
                    "maekawa_satisfied": str(maekawa_valid),
                    "kawasaki_satisfied": str(kawasaki_valid),
                    "maekawa_details": maekawa_details,
                    "kawasaki_details": kawasaki_details,
                }
                violations.append(violation)
                self._print_violation_details(
                    vertex,
                    maekawa_valid,
                    kawasaki_valid,
                    maekawa_details,
                    kawasaki_details,
                )

        return is_foldable, violations

    def _print_violation_details(
            self,
            vertex: Point,
            maekawa_valid: bool,
            kawasaki_valid: bool,
            maekawa_details: Dict,
            kawasaki_details: Dict,
        ) -> None:
            """Log detailed information about theorem violations at a vertex."""
            if not maekawa_valid:
                logger.warning("Maekawa's theorem violated at vertex (%f, %f):", vertex.x, vertex.y)
                logger.debug("Mountain creases: %d", maekawa_details['mountain_count'])
                logger.debug("Valley creases: %d", maekawa_details['valley_count'])
                logger.debug("Difference: %d (should be 2)", maekawa_details['difference'])

            if not kawasaki_valid:
                logger.warning("Kawasaki's theorem violated at vertex (%f, %f):", vertex.x, vertex.y)
                if "error" in kawasaki_details:
                    logger.debug("%s", kawasaki_details['error'])
                    logger.debug(
                        "Found %d creases, need %d",
                        kawasaki_details['angle_count'],
                        kawasaki_details['min_required']
                    )
                else:
                    logger.debug("Sum of odd angles: %.2f°", kawasaki_details['sum_odd'])
                    logger.debug("Sum of even angles: %.2f°", kawasaki_details['sum_even'])
                logger.debug("Difference: %.2f°", kawasaki_details['angle_difference'])
                logger.debug(
                    "Angles: %s",
                    [f'{a:.1f}°' for a in kawasaki_details['angles']]
                )
    def is_valid_pattern(self) -> Tuple[bool, Dict]:
        """Check if the pattern is valid by verifying flat-foldability and intersections."""
        is_foldable, violations = self.is_flat_foldable()
        intersections = self.check_crease_intersections()

        report = {
            "is_flat_foldable": is_foldable,
            "foldability_violations": violations,
            "has_intersections": len(intersections) > 0,
            "intersections": intersections,
        }

        is_valid = is_foldable and len(intersections) == 0
        return is_valid, report

    def remove_redundant_vertices(self) -> None:
        """Remove redundant vertices that don't affect the pattern's structure."""
        vertices_to_remove = []
        creases_to_remove = []
        creases_to_add = []

        # Identify vertices and creases to modify
        for vertex in self.vertices:
            connected_creases = self.get_connected_creases(vertex)
            if should_remove_vertex(vertex, connected_creases, self.grid_size):
                vertices_to_remove.append(vertex)
                creases_to_remove.extend(connected_creases)
                new_crease = merge_creases(vertex, connected_creases)
                if new_crease:
                    creases_to_add.append(new_crease)

        # Apply modifications
        self.creases = [c for c in self.creases if c not in creases_to_remove]
        self.creases.extend(creases_to_add)
        self.vertices = [v for v in self.vertices if v not in vertices_to_remove]
