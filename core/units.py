def mm(value):
    """Convert millimetres to Fusion's internal unit (centimetres).

    Example: mm(20) returns 2.0, which Fusion reads as 20 mm.
    """
    return value / 10.0

def to_mm(value):
    """Convert Fusion's internal unit (centimetres) back to millimetres.

    Example: to_mm(54.0) returns 540.0.
    """
    return value * 10.0

# sorry americans no freedom units
