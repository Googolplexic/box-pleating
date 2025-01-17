# box-pleating: [GitHub](https://github.com/Googolplexic/box-pleating), [PyPI](https://pypi.org/project/box-pleating/1.0.1/)


A Python package for creating, analyzing, and validating box-pleating origami patterns. Provides tools for working with box-pleating patterns including FOLD format conversion and flat-foldability validation.

[![PyPI version](https://badge.fury.io/py/box-pleating.svg)](https://badge.fury.io/py/box-pleating)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install box-pleating
```

## Quick Start

```python
from box_pleating import BoxPleatingPattern, Point, CreaseType
from box_pleating.fold import FoldConverter

# Create a new pattern with a 10x10 grid
pattern = BoxPleatingPattern(grid_size=10)

# Add creases
pattern.add_crease(
    Point(0, 0),
    Point(5, 5),
    CreaseType.MOUNTAIN
)

# Check if pattern is valid and flat-foldable
is_valid, report = pattern.is_valid_pattern()

# Convert to FOLD format
converter = FoldConverter()
fold_data = converter.to_fold(pattern)
```

## Features

### Box-Pleating Pattern Creation
- Create patterns on a customizable grid
- Add mountain, valley and border folds
- Automatic intersection and overlap handling
- Grid-based validation ensuring 45° and 90° angles (No Pythagorean Stretches, unfortunately)

### Pattern Validation
- Flat-foldability checking using:
  - Kawasaki's theorem (alternating angles sum to 180°)
  - Maekawa's theorem (mountain/valley crease difference is 2)
- Crease intersection detection
- Grid alignment verification, kind of

### FOLD Format Support
- Import from FOLD format
- Export to FOLD format
- Automatic grid size optimization, kind of
- Redundant vertex removal

### Coming Soon (Maybe)
- Crease removal/changing

## Detailed Usage

### Creating a Pattern

```python
from box_pleating import BoxPleatingPattern, Point, CreaseType

# Create a pattern with a 10x10 grid
pattern = BoxPleatingPattern(grid_size=10)

# Add a mountain fold
pattern.add_crease(
    Point(0, 0),  # Start point
    Point(5, 5),  # End point
    CreaseType.MOUNTAIN
)

# Add a valley fold
pattern.add_crease(
    Point(5, 5),
    Point(10, 5),
    CreaseType.VALLEY
)
```

### Converting FOLD Format

```python
from box_pleating.fold import FoldConverter

converter = FoldConverter()

# Load from FOLD file
pattern = converter.load_fold("input.fold")

# Save to FOLD file
converter.save_fold(pattern, "output.fold")
```

### Validating Patterns

```python
# Check flat-foldability
is_foldable, violations = pattern.is_flat_foldable()
if not is_foldable:
    print("Violations found:")
    for violation in violations:
        print(f"Vertex at ({violation['vertex']['x']}, {violation['vertex']['y']})")
        print(f"Maekawa satisfied: {violation['maekawa_satisfied']}")
        print(f"Kawasaki satisfied: {violation['kawasaki_satisfied']}")

# Check overall pattern validity
is_valid, report = pattern.is_valid_pattern()
```

### Pattern Cleanup

```python
# Remove redundant vertices (vertices where parallel creases of the same type meet)
pattern.remove_redundant_vertices()
```

## Contributing

Contributions are welcome.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

1. [FOLD file documentation](https://github.com/edemaine/fold/blob/main/doc/spec.md)
2. Toshikazu Kawasaki's Theorem on flat-foldability
3. Jun Maekawa's Theorem on mountain-valley assignments
4. My Graph Theory notes

## Authors

- Coleman Lai

## Acknowledgments

- The FOLD file project contributors
- Claude AI by Anthropic (for debugging/generation of some code)
