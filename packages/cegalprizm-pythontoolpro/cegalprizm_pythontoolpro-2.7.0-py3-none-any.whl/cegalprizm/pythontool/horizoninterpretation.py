# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.




import typing
import math
from cegalprizm.pythontool.chunk import Chunk
from cegalprizm.pythontool.petrelobject import PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory
from cegalprizm.pythontool.petrelobject import PetrelObjectWithPetrelNameSetter
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.primitives import Extent
from cegalprizm.pythontool import primitives
from cegalprizm.pythontool.chunktype import ChunkType
from cegalprizm.pythontool import _utils, horizoninterpretationutils
import cegalprizm.pythontool

if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.horizoninterpretation_grpc import HorizonInterpretationGrpc, HorizonProperty3dGrpc, HorizonInterpretation3dGrpc


class HorizonInterpretation(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter):
    """A class holding information about a Horizon Interpretation"""
    def __init__(self, python_petrel_property: "HorizonInterpretationGrpc"):
        super(HorizonInterpretation, self).__init__(python_petrel_property)
        self._extent = None
        self._horizoninterpretation_object_link = typing.cast("HorizonInterpretationGrpc", python_petrel_property)

    @property
    def horizon_interpretation_3ds(self) -> typing.List["HorizonInterpretation3d"]:
        return [HorizonInterpretation3d(po) for po in self._horizoninterpretation_object_link.GetHorizonInterpretation3dObjects()]

    @property
    @_utils.crs_wkt_decorator(object_type="HorizonInterpretation")
    def crs_wkt(self):
        return "Well-known text representation of coordinate reference systems not available for HorizonInterpretation objects."

    def __str__(self) -> str:
        """A readable representation of the HorizonInterpretation3D"""
        return 'HorizonInterpretation(petrel_name="{0}")'.format(self.petrel_name)

    @_utils.clone_docstring_decorator(return_type="HorizonInterpretation", respects_subfolders=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "HorizonInterpretation":
        return typing.cast("HorizonInterpretation", self._clone(name_of_clone, copy_values = copy_values))

class HorizonProperty3d(PetrelObject, PetrelObjectWithTemplate, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter):
    def __init__(self, python_petrel_property: "HorizonProperty3dGrpc"):
        super(HorizonProperty3d, self).__init__(python_petrel_property)
        self._extent: typing.Optional[Extent] = None
        self._horizonproperty3d_object_link = python_petrel_property
        self._shared_logic_helper = InterpretationSharedLogicHelper(self._horizonproperty3d_object_link, self)
        
    @property
    @horizoninterpretationutils.affine_transform_docstring_decorator
    def affine_transform(self):
        return self._shared_logic_helper.affine_transform

    @property
    @_utils.crs_wkt_decorator(object_type="HorizonProperty3d")
    def crs_wkt(self):
        return self._horizonproperty3d_object_link.GetCrs()

    @property
    @horizoninterpretationutils.extent_docstring_decorator
    def extent(self) -> Extent:
        return self._shared_logic_helper.extent

    @horizoninterpretationutils.indices_docstring_decorator
    def indices(self, x: float, y: float) -> primitives.Indices:
        return self._shared_logic_helper.indices(x, y)

    @horizoninterpretationutils.position_docstring_decorator
    def position(self, i: int, j: int) -> primitives.Point:
        return self._shared_logic_helper.position(i, j)

    @horizoninterpretationutils.is_undef_value_docstring_decorator
    def is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return self._shared_logic_helper._is_undef_value(value)

    @_utils.clone_docstring_decorator(return_type="HorizonProperty3d", respects_subfolders=True, continuous_template=True)
    def clone(self, name_of_clone: str, copy_values: bool = False, template: "Template" = None) -> "HorizonProperty3d":
        _utils.verify_continuous_clone(copy_values, template)
        return typing.cast("HorizonProperty3d",self._clone(name_of_clone, copy_values = copy_values, template = template))

    @property
    @horizoninterpretationutils.undef_value_docstring_decorator
    def undef_value(self) -> float:
        return self._shared_logic_helper._undef_value()

    @property
    @horizoninterpretationutils.unit_symbol_docstring_decorator
    def unit_symbol(self) -> typing.Optional[str]:
        return self._shared_logic_helper._unit_symbol()

    @horizoninterpretationutils.chunk_all_docstring_decorator_horizon_property_3d_decorator
    def all(self) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=None, j=None)

    @horizoninterpretationutils.chunk_docstring_decorator_horizon_property_3d_decorator
    def chunk(self, i: typing.Optional[typing.Tuple[int, int]] = None, j: typing.Optional[typing.Tuple[int, int]] = None) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=i, j=j)

    def __str__(self) -> str:
        """A readable representation of the HorizonProperty3D"""
        return 'HorizonProperty3D(petrel_name="{0}")'.format(self.petrel_name)

    @_utils.positions_doc_decorator_2d
    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[float], typing.List[float]]:
        return _utils.positions_to_ijks_2d(self._horizonproperty3d_object_link, positions)
    
    @_utils.ijks_doc_decorator_2d
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._horizonproperty3d_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @property
    def horizon_interpretation_3d(self) -> "HorizonInterpretation3d":
        """The parent 3d horizon interpretation of the horizon property.

        Returns:
            cegalprizm.pythontool.HorizonInterpretation3d: The parent grid of the property
        """   
        return HorizonInterpretation3d(self._horizonproperty3d_object_link.GetParentHorizonInterpretation3d())

    @_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

class HorizonInterpretation3d(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistory, PetrelObjectWithPetrelNameSetter):
    def __init__(self, interpretation_3d_grpc: "HorizonInterpretation3dGrpc"):
        super(HorizonInterpretation3d, self).__init__(interpretation_3d_grpc)
        self._extent = None
        self._horizoninterpretation3d_object_link = interpretation_3d_grpc
        self._shared_logic_helper = InterpretationSharedLogicHelper(self._horizoninterpretation3d_object_link, self)
        
    def __str__(self) -> str:
        """A readable representation of the HorizonInterpretation3d"""
        return 'HorizonInterpretation3D(petrel_name="{0}")'.format(self.petrel_name)

    @property
    @horizoninterpretationutils.affine_transform_docstring_decorator
    def affine_transform(self):
        return self._shared_logic_helper.affine_transform

    @property
    @_utils.crs_wkt_decorator(object_type="HorizonInterpretation3d")
    def crs_wkt(self):
        return self._horizoninterpretation3d_object_link.GetCrs()

    @property
    @horizoninterpretationutils.extent_docstring_decorator
    def extent(self) -> Extent:
        return self._shared_logic_helper.extent

    @horizoninterpretationutils.position_docstring_decorator
    def position(self, i: int, j: int) -> primitives.Point:
        return self._shared_logic_helper.position(i, j)

    @horizoninterpretationutils.is_undef_value_docstring_decorator
    def is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return self._shared_logic_helper._is_undef_value(value)

    @property
    @horizoninterpretationutils.undef_value_docstring_decorator
    def undef_value(self) -> float:
        return self._shared_logic_helper._undef_value()

    @property
    def sample_count(self) -> int:
        """The number of samples contained in the Horizon Interpretation 3d object.

        Returns:
            int: The number of points in the interpretation.
        """        
        return self._horizoninterpretation3d_object_link.SampleCount()

    @property
    def horizon_interpretation(self) -> HorizonInterpretation:
        """Returns the parent Horizon interpretation of the 3d horizon interpretation grid."""            
        return HorizonInterpretation(self._horizoninterpretation3d_object_link.GetParent())

    @property
    def horizon_property_3ds(self) -> typing.List[HorizonProperty3d]:
        """A readonly iterable collection of the 3d horizon interpretation properties for the 3d horizon interpretation grid 
        
        Returns:
            cegalprizm.pythontool.HorizonProperties:the 3d horizon interpretation properties
              for the 3d horizon interpretation grid"""
        return [
            HorizonProperty3d(po)
            for po in self._horizoninterpretation3d_object_link.GetAllHorizonPropertyValues()
        ]

    @_utils.clone_docstring_decorator(return_type="HorizonInterpretation3d", respects_subfolders=True)
    def clone(self, name_of_clone: str, copy_values: bool = False) -> "HorizonInterpretation3d":
        return typing.cast("HorizonInterpretation3d", self._clone(name_of_clone, copy_values = copy_values))

    @_utils.positions_doc_decorator_2d
    def positions_to_ijks(self, positions: typing.Union[typing.Tuple[typing.List[float], typing.List[float]], typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]])\
            -> typing.Tuple[typing.List[float], typing.List[float]]:
        return _utils.positions_to_ijks_2d(self._horizoninterpretation3d_object_link, positions)
    
    @_utils.ijks_doc_decorator_2d
    def ijks_to_positions(self, indices: typing.Tuple[typing.List[float], typing.List[float]]) -> typing.Tuple[typing.List[float], typing.List[float], typing.List[float]]:
        return _utils.ijks_to_positions(extent = self.extent, 
                                        object_link = self._horizoninterpretation3d_object_link, 
                                        indices = indices, 
                                        dimensions = 2)

    @_utils.get_template_decorator
    def get_template(self) -> typing.Union["Template", "DiscreteTemplate", None]:
        return self._get_template()

    @horizoninterpretationutils.chunk_docstring_decorator_horizon_interp_3d_decorator
    def chunk(self, i: typing.Optional[typing.Tuple[int, int]] = None, j: typing.Optional[typing.Tuple[int, int]] = None) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=i, j=j)

    @horizoninterpretationutils.chunk_all_docstring_decorator_horizon_interp_3d_decorator
    def all(self) -> Chunk:
        return self._shared_logic_helper._make_chunk(i=None, j=None)

    @horizoninterpretationutils.indices_docstring_decorator
    def indices(self, x: float, y: float) -> primitives.Indices:
        return self._shared_logic_helper.indices(x, y)

    @property
    @horizoninterpretationutils.unit_symbol_docstring_decorator
    def unit_symbol(self) -> typing.Optional[str]:
        return self._shared_logic_helper._unit_symbol()

class InterpretationSharedLogicHelper():
    def __init__(self, grpc_object_link, python_petrel_object):
        self._extent: typing.Optional[Extent] = None
        self._object_link = grpc_object_link
        self._python_petrel_object = python_petrel_object

    @property
    def affine_transform(self):
        return _utils.from_backing_arraytype(
            self._object_link.GetAffineTransform()
        )

    def indices(self, x: float, y: float) -> primitives.Indices:
        index2 = self._object_link.IndexAtPosition(x, y)
        if index2 is None:
            raise ValueError("Position not in horizon property")
        if (
            index2 is None
            or index2.GetValue().I < 0
            or index2.GetValue().J < 0
            or index2.GetValue().I >= self.extent.i
            or index2.GetValue().J >= self.extent.j
        ):
            raise ValueError("Position not in horizon property")
        return primitives.Indices(index2.GetValue().I, index2.GetValue().J, None)

    @property
    def extent(self) -> Extent:
        if self._extent is None:
            i = self._object_link.NumI()
            j = self._object_link.NumJ()
            self._extent = Extent(i=i, j=j, k=1)

        return self._extent

    def position(self, i: int, j: int) -> primitives.Point:
        point3 = self._object_link.PositionAtIndex(i, j)
        if point3 is None:
            raise ValueError("Index not valid for interpretation")
        return primitives.Point(
            point3.GetValue().X, point3.GetValue().Y, point3.GetValue().Z
        )

    def _is_undef_value(self, value: typing.Union[float, int]) -> bool:
        return math.isnan(value)

    def _unit_symbol(self) -> typing.Optional[str]:
        return _utils.str_or_none(self._object_link.GetDisplayUnitSymbol())

    def _undef_value(self) -> float:
        return float("nan")

    def _make_chunk(self, i=None, j=None) -> "cegalprizm.pythontool.Chunk":
        value_getters = {
            ChunkType.k: lambda i, j, k: _utils.from_backing_arraytype(
                self._object_link.GetChunk(i, j)
            )
        }
        value_setters = {
            ChunkType.k: lambda i, j, k, values: self._object_link.SetChunk(
                i, j, _utils.to_backing_arraytype(values)
            )
        }
        value_shapers = {
            ChunkType.k: lambda i, j, k, values: _utils.ensure_2d_float_array(
                values, i, j
            )
        }
        value_accessors = {ChunkType.k: lambda i, j, k: _utils.native_accessor((i, j))}

        return Chunk(
            i,
            j,
            None,
            self._python_petrel_object,
            self.extent,
            value_getters,
            value_setters,
            value_shapers,
            value_accessors,
            (True, True, False),
            ChunkType.k,
            readonly=self._python_petrel_object.readonly,
        )