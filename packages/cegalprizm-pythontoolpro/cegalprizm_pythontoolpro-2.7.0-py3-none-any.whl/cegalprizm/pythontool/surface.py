# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from warnings import warn

import cegalprizm.pythontool
import math
import pandas as pd
from cegalprizm.pythontool import _utils
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithHistoryToBeDeprecated
from cegalprizm.pythontool import PetrelObjectWithPetrelNameSetter
from cegalprizm.pythontool import _config
from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool.chunktype import ChunkType
from cegalprizm.pythontool.template import Template, DiscreteTemplate

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.surface_grpc import SurfaceCollectionGrpc, SurfaceDiscretePropertyGrpc, SurfaceGrpc, SurfacePropertyGrpc

class Surface(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter):
    def __init__(self, petrel_object_link: "SurfaceGrpc"):
        super(Surface, self).__init__(petrel_object_link)
        self._surface_object_link = petrel_object_link
        self.__extent: typing.Optional[primitives.Extent] = None    

    @property
    def affine_transform(self):
        """ The affine transform of the object.

        returns:
            1d array: An array with 6 coefficients of the affine transformation matrix. If array is
            represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of
            form:
            | a b e |
            | c d f |
            | 0 0 1 |
        """
        return _utils.from_backing_arraytype(
            self._surface_object_link.GetAffineTransform()
        )

    @property
    @_utils.crs_wkt_decorator(object_type="Surface")
    def crs_wkt(self):
        return self._surface_object_link.GetCrs()

    @property
    def extent(self) -> primitives.Extent:
        """The number of surface nodes in the i and j directions.

        Returns:
            `cegalprizm.pythontool.Extent`: The number of surface nodes in each direction.
        """
        if self.__extent is None:
            i = self._surface_object_link.NumI()
            j = self._surface_object_link.NumJ()
            self.__extent = cegalprizm.pythontool.Extent(i=i, j=j, k=1)

        return self.__extent

    def __str__(self) -> str:
        """A readable representation of the Surface"""
        return "Surface(petrel_name=\"{0}\")".format(self.petrel_name)

    def indices(self, x: float, y: float) -> primitives.Indices:
        """The indices of the surface node nearest the specified point

        Note: the node indices are 0-based, but in the Petrel
        UI they are 1-based.

        Args:
            x: the x-coordinate
            y: the y-coordinate

        Raises:
            ValueError: if the point is outside the beyond the extent
                        of the surface

        Returns:
            A :class:`cegalprizm.pythontool.primitives.Indices` object
            representing the indices of the node nearest the point.
            `k` will always be `None`.
        """
        index2 = self._surface_object_link.IndexAtPosition(x, y)
        if index2 is None:
            raise ValueError("position not in surface")
        if index2 is None or \
           index2.GetValue().I < 0 or \
           index2.GetValue().J < 0 or \
           index2.GetValue().I >= self.extent.i or \
           index2.GetValue().J >= self.extent.j:
            raise ValueError("position not in surface")
        return primitives.Indices(index2.GetValue().I, index2.GetValue().J, None)

    def position(self, i: int, j: int) -> primitives.Point:
        """The xyz position of the surface node

        Args:
            i: the i-index of the surface node
            j: the j -index of the surface node

        Raises:
            ValueError: if the indices are outside the surface

        Returns:
            A :class:`cegalprizm.pythontool.Point` object
            representing the xyz position of the surface node.
        """
        point3 = self._surface_object_link.PositionAtIndex(i, j)
        if point3 is None:
            raise ValueError("Index not valid for surface")
        return primitives.Point(
            point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z
        )

    def as_dataframe(self, dropna: bool = False) -> pd.DataFrame:
        """Get a dataframe with the I, J, X, Y and Z values of the surface nodes.

        The values in the Z column will be in either time or depth units, depending on the domain of the surface.

        Note:
            surface.as_dataframe() prints out all Is and Js of a regular 2-dimensional grid covering the extent of the surface. This means many Z-values might show up as NaN because no Z value is defined in Petrel. Set the dropna parameter to True to drop all rows where Z is NaN.

        **Example:**
        
        Retrieve the dataframe and drop all rows where Z is NaN

        .. code-block:: Python

            surface = petrellink.surfaces["Input/Path/To/Surface"]
            df = surface.as_dataframe(dropna=True)
        
        Returns:
            pd.DataFrame: A dataframe with the I, J, X, Y and Z values of the surface nodes

        Raises:
            ValueError: if the dropna parameter is not a boolean
        """
        if not isinstance(dropna, bool):
            raise ValueError("dropna must be a boolean")
        return self._surface_object_link.GetPositionsDataframe(dropna)

    @property
    def coords_extent(self) -> primitives.CoordinatesExtent:
        """The extent of the object in world-coordinates

        Returns:
            cegalprizm.pythontool.CoordinatesExtent: the extent of the object in world-coordinate
        """
        return primitives.CoordinatesExtent(self._surface_object_link.AxesRange())

    @property
    def parent_collection(self) -> "Surfaces":
        """The parent collection containing this surface.

        Iterating through this collection will return this surface and all its siblings in the Petrel Input Tree.

        Returns:

            cegalprizm.pythontool.Surfaces: the parent collection
        """

        return Surfaces(self._surface_object_link.ParentSurfaceCollection())

    @property
    def surface_attributes(self) -> "SurfaceAttributes":
        """The attributes for this surface

        Returns:

            cegalprizm.pythontool.SurfaceAttributes: the attributes for the surface
        """
        surface_properties = self._surface_object_link.GetSurfaceProperties()
        surface_dict_properties = self._surface_object_link.GetDictionarySurfaceProperties()
        
        return SurfaceAttributes(self, surface_properties, surface_dict_properties)

    @_utils.positions_doc_decorator_2d
    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[float], typing.List[float]]:
        return _utils.positions_to_ijks_2d(self._surface_object_link, positions)

    @_utils.ijks_doc_decorator_2d
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]])\
            -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._surface_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class SurfaceAttributes():
    """A readonly iterable collection of a set of surface attributes

    This example prints out all sibling attributes of a particular attribute:

    **Example:**

        .. code-block:: Python

            all_attributes = my_attr.surface.surface_attributes
            for attr in all_attributes:
                if attr != my_attr:
                    print(attr)

    """
    def __init__(self, parent, surface_properties, surface_dict_properties):
        self._parent_obj = parent
        self._surface_attributes = []

        for attr in surface_properties:
            self._surface_attributes.append(SurfaceAttribute(attr))
        for attr in surface_dict_properties:
            self._surface_attributes.append(SurfaceDiscreteAttribute(attr))
        
    def __len__(self) -> int:
        return len(self._surface_attributes)

    def __iter__(self) -> typing.Iterable[typing.Union["SurfaceAttribute", "SurfaceDiscreteAttribute"]]:
        return iter(self._surface_attributes)

    def __str__(self) -> str:
        return 'SurfaceAttributes({0}="{1}")'.format(self._parent_obj._petrel_object_link._sub_type, self._parent_obj)

    def __repr__(self) -> str:
        return str(self)

class Surfaces(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated):
    """A readonly collection of  a set of surfaces.

    Although this object wraps a Petrel collection, it does not support any operations on it apart from iterating through its contents.
    """

    def __init__(self, petrel_object_link: "SurfaceCollectionGrpc"):
        super(Surfaces, self).__init__(petrel_object_link)
        self._surfaces_object_link = petrel_object_link
        
    def __len__(self) -> int:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return len(surfaces)

    def __iter__(self) -> typing.Iterable[Surface]:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return iter(surfaces)

    def __getitem__(self, idx: int) -> Surface:
        surfaces = []
        for surface in self._surfaces_object_link.GetRegularHeightFieldObjects():
            s = Surface(surface)
            surfaces.append(s)
        return surfaces[idx] # type: ignore

    def __str__(self) -> str:
        """A readable representation of the Surfaces collection"""
        return 'Surfaces(petrel_name="{0}")'.format(self.petrel_name)


class SurfaceAttribute(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter):

    def __init__(self, petrel_object_link: "SurfacePropertyGrpc"):
        super(SurfaceAttribute, self).__init__(petrel_object_link)
        self._surfaceattribute_object_link = petrel_object_link

    @property
    def affine_transform(self):
        """ The affine transform of the object.

        returns:
            1d array: An array with 6 coefficients of the affine transformation matrix. If array is
            represented as [a, b, c, d, e, f] then this corresponds to a affine transformation matrix of
            form:
            | a b e |
            | c d f |
            | 0 0 1 |
        """
        return _utils.from_backing_arraytype(
            self._surfaceattribute_object_link.GetAffineTransform()
        )

    @property
    @_utils.crs_wkt_decorator(object_type="SurfaceAttribute")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for SurfaceAttribute objects"

    def __str__(self) -> str:
        """A readable representation of the SurfaceAttribute"""
        return 'SurfaceAttribute(petrel_name="{0}")'.format(self.petrel_name)

    def is_undef_value(self, value: typing.Union[int, float]) -> bool:
        """Whether the value is the 'undefined value' for the attribute

        Petrel represents some undefined values by ``MAX_INT``, others
        by ``NaN``.  A comparison with ``NaN`` will always return
        ``False`` (e.g. ``float.nan != float.nan``) so it is
        preferable to always use this method to test for undefined
        values.

        Args:
            value: the value to test

        Returns:
            bool: True if value is 'undefined' for this surface
            attribute

        """
        return self._is_undef_value(value)

    @property
    def undef_value(self) -> float:
        """The 'undefined value' for this attribute

        Use this value when setting a slice's value to 'undefined'.
        Do not attempt to test for undefinedness by comparing with
        this value, use :meth:`is_undef_value` instead.

        Returns:
           The 'undefined value' for this attribute
        """
        return self._undef_value()

    def _undef_value(self) -> float:
        return float("nan")

    @property
    def unit_symbol(self) -> typing.Optional[str]:
        """The symbol for the unit which the values are measured in

        Returns:

            string: The symbol for the unit, or None if no unit is used
        """
        return self._unit_symbol()

    @_utils.clone_docstring_decorator(return_type="SurfaceAttribute", respects_subfolders=True, continuous_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "SurfaceAttribute":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("SurfaceAttribute", self._clone(name_of_clone, copy_values = copy_values, template = template))

    def _unit_symbol(self) -> typing.Optional[str]:
        return _utils.str_or_none(self._surfaceattribute_object_link.GetDisplayUnitSymbol())

    def _is_undef_value(self, value: typing.SupportsFloat) -> bool:
        return math.isnan(value)

    @property
    def parent_surface(self) -> None:
        """DeprecationWarning: 'parent_surface' has been removed. Use 'surface' instead
        """
        warn("'parent_surface' has been removed. Use 'surface' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'parent_surface' has been removed. Use 'surface' instead")

    @property
    def surface(self) -> Surface:
        """The parent surface of the attribute

        Returns:

            cegalprizm.pythontool.Surface: The parent surface of the attribute
        """
        parent = self._surfaceattribute_object_link.GetParentSurface()
        parent_s = Surface(parent)

        return parent_s 

    def all(self) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the attribute

        Returns:

            cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the attribute
        """
        return self._make_chunk(i = None, j = None)

    def chunk(self, irange: typing.Tuple[int, int] = None, jrange: typing.Tuple[int, int] = None) -> Chunk:
        """Creates a :class:`cegalprizm.pythontool.Chunk` with the values for the attribute

        Args:
            i: A tuple(i1,i2) where i1 is the start index and i2 is the end index. 
                The start and end value in this range is inclusive. If None include all i values.
            j: A tuple(j1,j2) where j1 is the start index and j2 is the end index. 
                The start and end value in this range is inclusive. If None include all j values.

        Returns:

            cegalprizm.pythontool.Chunk:  A `Slice` containing the values for the attribute
        """
        return self._make_chunk(i=irange, j=jrange)

    def _make_chunk(self, i=None, j=None) -> Chunk:
        extent = self.surface.extent
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._surfaceattribute_object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._surfaceattribute_object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_float_array(
                values, i, j
            )
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return cegalprizm.pythontool.Chunk(
            i,
            j,
            None,
            self,
            extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self.readonly,
        )

    def has_same_parent(self, other: "SurfaceAttribute") -> bool:
        """Tests whether the surface attribute has the same parent surface

        Args:
            other: the other surface attribute

        Returns:
            bool: ``True`` if the ``other`` object has the same parent surface

        Raises:
            ValueError: if ``other`` is not a SurfaceAttribute
        """
        if not isinstance(other, SurfaceAttribute):
            raise ValueError("can only compare parent with other SurfaceAttribute")
        return ( 
            self.surface._surface_object_link.GetDroidString()
            == other.surface._surface_object_link.GetDroidString()
        )

    @_utils.positions_doc_decorator_2d
    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]]) \
            -> typing.Tuple[typing.List[float], typing.List[float]]:
        return _utils.positions_to_ijks_2d(self._surfaceattribute_object_link, positions)

    @_utils.ijks_doc_decorator_2d
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        return _utils.ijks_to_positions(extent = self.surface.extent, 
                                        object_link = self._surfaceattribute_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class SurfaceDiscreteAttribute(SurfaceAttribute):

    def __init__(self, petrel_object_link: "SurfaceDiscretePropertyGrpc"):
        super(SurfaceDiscreteAttribute, self).__init__(petrel_object_link)
        self._surfacediscreteattribute_object_link = petrel_object_link
        self._discrete_codes = None

    def __str__(self) -> str:
        """A readable representation of the SurfaceDiscreteAttribute"""
        return 'SurfaceDiscreteAttribute(petrel_name="{0}")'.format(self.petrel_name)

    def _unit_symbol(self) -> None:
        return None

    @property
    def discrete_codes(self) -> typing.Dict[str, str]:
        """A dictionary of discrete codes and values

        Changes to this dictionary will not be persisted or affect any Petrel objects.

        **Example:**

        .. code-block:: Python

            myattr = petrellink.surface_discrete_attributes['facies']
            print(myattr.discrete_codes[1])
            # outputs 'Fine sand'
        """
        if self._discrete_codes is None:
            self._discrete_codes = self.__make_discrete_codes_dict()
        return self._discrete_codes

    @property
    @_utils.crs_wkt_decorator(object_type="SurfaceDiscreteAttribute")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for SurfaceDiscreteAttribute objects"

    @_utils.clone_docstring_decorator(return_type="SurfaceDiscreteAttribute", respects_subfolders=True, discrete_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, discrete_template: "DiscreteTemplate" = None) -> "SurfaceDiscreteAttribute":
        _utils.verify_discrete_clone(copy_values, discrete_template)
        return typing.cast("SurfaceDiscreteAttribute", self._clone(name_of_clone, copy_values = copy_values, template = discrete_template))

    def _undef_value(self) -> int:
        return _config._INT32MAXVALUE

    def _is_undef_value(self, value) -> bool:
        return value == _config._INT32MAXVALUE

    def __make_discrete_codes_dict(self) -> typing.Dict[int, str]:
        codes = {}
        for tup in self._surfacediscreteattribute_object_link.GetAllDictionaryCodes():
            k = tup.Item1
            v = tup.Item2
            codes[k] = v
        return codes

    def _make_chunk(self, i=None, j=None):
        extent = self.surface.extent
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._surfacediscreteattribute_object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._surfacediscreteattribute_object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_int_array(values, i, j)
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return cegalprizm.pythontool.Chunk(
            i,
            j,
            None,
            self,
            extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self.readonly,
        )

