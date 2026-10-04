def mm(value):
    """Convert millimetres to Fusion's internal unit (centimetres).

    Example: mm(20) returns 2.0, which Fusion reads as 20 mm.
    """
    return value / 10.0
