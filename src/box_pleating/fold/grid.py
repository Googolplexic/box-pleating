from typing import List


def _prime_factors(n: int) -> List[int]:
    """Get prime factors of a number in ascending order."""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors


def _get_grid_possibilities(max_grid: int = 100) -> List[int]:
    """
    Generate possible grid sizes from combinations of small prime factors.

    Args:
        max_grid: Maximum allowed grid size

    Returns:
        List of valid grid sizes derived from prime factor combinations
    """
    # Common prime factors in origami patterns
    base_primes = [2, 3, 5, 7, 11]

    grids = set()

    def generate_combinations(current: int, prime_idx: int):
        if current > max_grid:
            return
        if current >= 2:  # Valid grid sizes start from 2
            grids.add(current)
        if prime_idx >= len(base_primes):
            return

        # Try using current prime 1 or more times
        prime = base_primes[prime_idx]
        next_val = current
        while next_val * prime <= max_grid:
            next_val *= prime
            generate_combinations(next_val, prime_idx + 1)

        # Try without using current prime
        generate_combinations(current, prime_idx + 1)

    generate_combinations(1, 0)
    return sorted(list(grids))


def _is_reasonable_grid_size(grid_size: int, max_grid: int = 100) -> bool:
    """
    Check if a grid size is reasonable for origami patterns.

    Args:
        grid_size: Proposed grid size to check
        max_grid: Maximum allowed grid size

    Returns:
        bool: True if grid size is reasonable
    """
    if not (2 <= grid_size <= max_grid):
        return False

    # Check if composed of reasonable prime factors
    factors = _prime_factors(grid_size)
    reasonable_primes = {2, 3, 5, 7, 11}
    return all(p in reasonable_primes for p in factors)


def compute_optimal_grid_size(
    vertices: List[List[float]], edges: List[List[int]], max_grid: int = 100
) -> int:
    """
    Compute optimal grid size based on pattern geometry using prime factor analysis.

    Args:
        vertices: List of [x, y] coordinate pairs
        edges: List of [vertex1_idx, vertex2_idx] pairs
        max_grid: Maximum allowed grid size

    Returns:
        int: Optimal grid size
    """
    if not vertices:
        return 1  # Empty pattern
    if len(vertices) == 1:
        return 1  # Single point
    if len(vertices) == 2 and len(edges) == 1:
        return 2  # Single line

    # Find pattern dimensions
    xs = [x for x, _ in vertices]
    ys = [y for _, y in vertices]
    x_range = max(xs) - min(xs)
    y_range = max(ys) - min(ys)
    max_range = max(x_range, y_range)

    # Find minimum spacing between vertices
    from .geometry import compute_minimum_spacing

    min_spacing = compute_minimum_spacing(vertices)

    # Direct calculation of grid size
    measured_grid = round(max_range / min_spacing)

    # If measured grid is reasonable, use it
    if _is_reasonable_grid_size(measured_grid, max_grid):
        return measured_grid

    # Otherwise find closest valid grid size
    valid_grids = _get_grid_possibilities(max_grid)
    target_spacing = min_spacing

    best_grid = None
    best_error = float("inf")

    for grid in valid_grids:
        spacing = max_range / grid
        error = abs(spacing - target_spacing)

        # Prefer simpler grids when errors are similar
        complexity_penalty = len(_prime_factors(grid)) * 0.1
        adjusted_error = error + complexity_penalty

        if adjusted_error < best_error:
            best_error = adjusted_error
            best_grid = grid

    return best_grid if best_grid is not None else 2


def snap_to_grid(value: float, grid_size: int) -> int:
    """Snap a value to the nearest grid point while preserving relative positions."""
    grid_value = value * grid_size
    return int(round(grid_value))

