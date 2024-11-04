import json
from typing import Dict
from ..models import Point, CreaseType
from ..pattern import BoxPleatingPattern
from .geometry import compute_faces_vertices
from .grid import compute_optimal_grid_size


class FoldConverter:
    """
    Converter class for translating between BoxPleatingPattern and FOLD format.

    The FOLD format is a standard file format for origami crease patterns
    (see https://github.com/edemaine/fold).
    """


    def from_fold(self, fold_data: Dict) -> BoxPleatingPattern:
        """Create BoxPleatingPattern from FOLD format with minimal grid size.

        Args:
            fold_data (Dict): FOLD format data dictionary

        Returns:
            BoxPleatingPattern: New pattern instance

        Note:
            Handles missing or empty data by creating an empty pattern
        """
        # Extract vertices and edges, defaulting to empty lists if missing
        vertices = fold_data.get("vertices_coords", [])
        edges = fold_data.get("edges_vertices", [])

        # Calculate optimal grid size without pre-scaling
        grid_size = compute_optimal_grid_size(vertices, edges)
        pattern = BoxPleatingPattern(grid_size)

        # If no vertices, return empty pattern
        if not vertices:
            return pattern

        vertex_points = []

        # Find coordinate ranges
        xs = [x for x, _ in vertices]
        ys = [y for _, y in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Calculate ranges, handling zero cases
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1

        # Scale factor to preserve relative distances
        scale = min(grid_size / x_range, grid_size / y_range)

        for x, y in vertices:
            # Scale and shift coordinates to fit grid
            grid_x = round((x - min_x) * scale)
            grid_y = round((y - min_y) * scale)

            vertex_points.append(Point(grid_x, grid_y))

        # Add edges with appropriate crease types if any exist
        for v1_idx, v2_idx in edges:
            # Get crease assignment, defaulting to "U" (unassigned)
            assignment = "U"
            if "edges_assignment" in fold_data:
                try:
                    assignment = fold_data["edges_assignment"][
                        edges.index([v1_idx, v2_idx])
                    ]
                except (IndexError, ValueError):
                    pass

            crease_type = CreaseType.NONE
            if assignment == "M":
                crease_type = CreaseType.MOUNTAIN
            elif assignment == "V":
                crease_type = CreaseType.VALLEY

            start = vertex_points[v1_idx]
            end = vertex_points[v2_idx]
            pattern.add_crease(start, end, crease_type)

        return pattern

    def to_fold(self, pattern: BoxPleatingPattern) -> Dict:
        """Export BoxPleatingPattern to FOLD format."""
        # Convert vertices to FOLD coordinates
        vertices_coords = []
        vertex_map = {}
        for vertex in pattern.vertices:
            vertex_map[vertex] = len(vertices_coords)
            x = (vertex.x - pattern.grid_size / 2) * (400 / pattern.grid_size)
            y = (vertex.y - pattern.grid_size / 2) * (400 / pattern.grid_size)
            vertices_coords.append([x, y])

        # Convert creases to FOLD edges
        edges_vertices = []
        edges_assignment = []
        edges_foldAngle = []

        for crease in pattern.creases:
            v1 = vertex_map[crease.start]
            v2 = vertex_map[crease.end]
            edges_vertices.append([v1, v2])

            if crease.type == CreaseType.MOUNTAIN:
                edges_assignment.append("M")
                edges_foldAngle.append(-180)
            elif crease.type == CreaseType.VALLEY:
                edges_assignment.append("V")
                edges_foldAngle.append(180)
            else:
                edges_assignment.append("B")
                edges_foldAngle.append(0)

        # Compute additional FOLD properties
        faces_vertices = compute_faces_vertices(vertices_coords, edges_vertices)

        # Build vertices_vertices from edges
        vertices_vertices = [[] for _ in range(len(vertices_coords))]
        for v1, v2 in edges_vertices:
            vertices_vertices[v1].append(v2)
            vertices_vertices[v2].append(v1)

        for neighbors in vertices_vertices:
            neighbors.sort()

        # Create FOLD format dictionary
        return {
            "file_spec": 1.1,
            "file_creator": "BoxPleatingPattern Converter",
            "file_classes": ["creasePattern"],
            "frame_classes": ["creasePattern"],
            "vertices_coords": vertices_coords,
            "edges_vertices": edges_vertices,
            "edges_assignment": edges_assignment,
            "edges_foldAngle": edges_foldAngle,
            "vertices_vertices": vertices_vertices,
            "faces_vertices": faces_vertices,
        }

    def save_fold(self, pattern: BoxPleatingPattern, filename: str) -> None:
        """Save BoxPleatingPattern to FOLD file."""
        fold_data = self.to_fold(pattern)
        with open(filename, "w") as f:
            json.dump(fold_data, f, indent=2)

    def load_fold(self, filename: str) -> BoxPleatingPattern:
        """Load BoxPleatingPattern from FOLD file."""
        with open(filename, "r") as f:
            fold_data = json.load(f)
        return self.from_fold(fold_data)
