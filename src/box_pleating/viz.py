"""Crease pattern visualization.

Renders a BoxPleatingPattern with matplotlib using conventional notation:

- Mountain creases: red, solid.
- Valley creases: blue, dashed.
- Border: light gray, solid, thicker.
- Origin at lower-left, y increasing up.
"""

from __future__ import annotations

from typing import Optional

from .models import CreaseType
from .pattern import BoxPleatingPattern

_STYLE = {
    CreaseType.MOUNTAIN: dict(color="red", linestyle="-", linewidth=1.5),
    CreaseType.VALLEY: dict(color="blue", linestyle="--", linewidth=1.5),
    CreaseType.BORDER: dict(color="lightgray", linestyle="-", linewidth=2.5),
}


def render_matplotlib(
    pattern: BoxPleatingPattern,
    ax=None,
    show_vertices: bool = False,
):
    """Render a crease pattern using matplotlib.

    Args:
        pattern: The BoxPleatingPattern to draw.
        ax: An existing matplotlib Axes. If None, a new figure and axes
            are created.
        show_vertices: When True, draw a small dot at every vertex.

    Returns:
        The matplotlib Axes used for drawing.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(4, 4))

    g = pattern.grid_size
    if g is not None:
        ax.plot(
            [0, g, g, 0, 0],
            [0, 0, g, g, 0],
            color="lightgray",
            linewidth=2.5,
        )

    for crease in pattern.creases:
        style = _STYLE.get(crease.type)
        if style is None:
            continue
        ax.plot(
            [crease.start.x, crease.end.x],
            [crease.start.y, crease.end.y],
            **style,
        )

    if show_vertices:
        xs = [v.x for v in pattern.vertices]
        ys = [v.y for v in pattern.vertices]
        ax.plot(xs, ys, "ko", markersize=3)

    if g is not None:
        ax.set_xlim(-0.5, g + 0.5)
        ax.set_ylim(-0.5, g + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    return ax
