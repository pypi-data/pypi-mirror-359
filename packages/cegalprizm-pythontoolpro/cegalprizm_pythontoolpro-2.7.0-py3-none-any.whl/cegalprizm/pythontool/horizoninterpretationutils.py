# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




def affine_transform_docstring_decorator(func):
    func.__doc__ = affine_transform_docstring()
    return func

def affine_transform_docstring() -> str:
    return """ The affine transform of the object.

    returns:
        1d array: An array with 6 coefficients of the affine transformation matrix.
        If array is represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of form:

        | a b e |
        | c d f |
        | 0 0 1 |
    """

def chunk_all_docstring_decorator_horizon_property_3d_decorator(func):
    func.__doc__ = chunk_all_docstring("Horizon Property 3D object")
    return func

def chunk_all_docstring_decorator_horizon_interp_3d_decorator(func):
    func.__doc__ = chunk_all_docstring("Horizon Interpretation 3D object")
    return func

def chunk_all_docstring(object_description: str) -> str:
    return f"""Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the {object_description}.

    Returns:
        cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the {object_description}
    """

def chunk_docstring_decorator_horizon_property_3d_decorator(func):
    func.__doc__ = chunk_docstring("Horizon Property 3D object")
    return func

def chunk_docstring_decorator_horizon_interp_3d_decorator(func):
    func.__doc__ = chunk_docstring("Horizon Interpretation 3D object")
    return func

def chunk_docstring(object_description: str) -> str:
    return f"""Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the {object_description}.

    Args:
        i: A tuple(i1,i2) where i1 is the start index and i2 is the end index. 
            The start and end value in this range is inclusive. If None include all i values.
        j: A tuple(j1,j2) where j1 is the start index and j2 is the end index. 
            The start and end value in this range is inclusive. If None include all j values.

    Returns:
        cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the {object_description}
    """

def extent_docstring_decorator(func):
    func.__doc__ = extent_docstring()
    return func

def extent_docstring() -> str:
    return """The number of nodes in the i and j directions

    Returns:
        A :class:`cegalprizm.pythontool.Extent` object
    """

def indices_docstring_decorator(func):
    func.__doc__ = indices_docstring()
    return func

def indices_docstring() -> str:
    return """The indices of the node nearest the specified point

    Please note: the node indices are 0-based, but in the Petrel UI they are 1-based.

    Args:
        x: the x-coordinate
        y: the y-coordinate

    Returns:
        A :class:`cegalprizm.pythontool.primitives.Indices` object representing the indices of the node nearest the point.
        `K` will always be `None`.

    Raises:
        ValueError: if the point is outside the beyond the extent of the horizon property

    """

def is_undef_value_docstring_decorator(func):
    func.__doc__ = is_undef_value_docstring()
    return func

def is_undef_value_docstring() -> str:
    return """Whether the value is the 'undefined value' for the attribute

    Petrel represents some undefined values by ``MAX_INT``, others by ``NaN``.
    A comparison with ``NaN`` will always return ``False`` (e.g. ``float.nan != float.nan``) so it is preferable to always use this method to test for undefined values.

    Args:
        value: the value to test

    Returns:
        bool: True if value is 'undefined' for this horizon property attribute

    """

def position_docstring_decorator(func):
    func.__doc__ = position_docstring()
    return func

def position_docstring() -> str:
    return """The position of the node

    Args:
        i: the i-index of the node
        j: the j -index of the node

    Returns: A :class:`cegalprizm.pythontool.Point` object representing the position of the node.

    Raises:
        ValueError: if the indices are outside the horizon property
    """

def undef_value_docstring_decorator(func):
    func.__doc__ = undef_value_docstring()
    return func

def undef_value_docstring() -> str:
    return """The 'undefined value' for this attribute

    Use this value when setting a slice's value to 'undefined'.
    Do not attempt to test for undefinedness by comparing with this value, use :meth:`is_undef_value` instead.

    Returns:
        The 'undefined value' for this attribute
    """

def unit_symbol_docstring_decorator(func):
    func.__doc__ = unit_symbol_docstring()
    return func

def unit_symbol_docstring() -> str:
    return """The symbol for the unit which the values are measured in

    Returns:
        string: The symbol for the unit, or None if no unit is used
    """