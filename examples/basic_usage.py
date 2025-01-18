import logging
from box_pleating import BoxPleatingPattern, Point, CreaseType, configure_logger
from box_pleating.fold import FoldConverter

def create_simple_pattern():
    """Create a simple box-pleating pattern."""
    pattern = BoxPleatingPattern(8)
    
    # Create a simple mountain-valley pattern
    p1 = Point(0, 0)
    p2 = Point(4, 4)
    p3 = Point(8, 8)
    p4 = Point(0, 8)
    
    pattern.add_crease(p1, p2, CreaseType.MOUNTAIN)
    pattern.add_crease(p2, p3, CreaseType.VALLEY)
    pattern.add_crease(p2, p4, CreaseType.MOUNTAIN)
    
    return pattern

def main():
    # Enable detailed logging
    configure_logger(logging.DEBUG)
    
    # Create and validate a pattern
    pattern = create_simple_pattern()
    
    # Check if pattern is valid
    is_valid, report = pattern.is_valid_pattern()
    print(f"\nPattern validation:")
    print(f"Valid: {is_valid}")
    if not is_valid:
        print("Violations found:")
        for violation in report.get('foldability_violations', []):
            print(f"- At vertex {violation['vertex']}")
    
    # Save to FOLD format
    converter = FoldConverter()
    converter.save_fold(pattern, "simple_pattern.fold")
    print("\nPattern saved to 'simple_pattern.fold'")
    
    # Load back and verify
    loaded_pattern = converter.load_fold("simple_pattern.fold")
    print("\nPattern loaded successfully")
    print(f"Number of vertices: {len(loaded_pattern.vertices)}")
    print(f"Number of creases: {len(loaded_pattern.creases)}")

if __name__ == "__main__":
    main()
