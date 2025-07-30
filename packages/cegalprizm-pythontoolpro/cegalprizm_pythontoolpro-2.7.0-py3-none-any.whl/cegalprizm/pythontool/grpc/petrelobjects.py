# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from . import utils

class PetrelObjectStoreBase(dict):
    """Base class of read-only collections storing Petrel objects by their path.
    When iterated over, the objects are returned, not their paths (unlike a standard
    Python dictionary which returns the keys).
    """

    def __init__(self, petrelconnection):
        self._petrelconnection = petrelconnection
        self._objects = self._query_objects(petrelconnection)

    def _query_objects(self, petrelconnection):
        # Virtual method to be implemented in sub class
        return {}

    def get_petrel_objects(self, objects_info, find_object_by_guid_func):
        objects = {}
        for guid, path in objects_info.items():
            obj = find_object_by_guid_func(guid)

            if path in objects.keys():
                # duplicate paths!
                existing = objects[path]
                # create or append to a list of petrel objects
                if isinstance(existing, list):
                    existing.append(obj)
                else:
                    objects[path] = [existing, obj]
            else:
                # unique path
                objects[path] = obj
        return objects

    def get_petrel_object_from_ref(self, object_refs, find_object_by_obj_ref_func):
        objects = {}
        for objref in object_refs:
            path = objref.path # fetch path from objref instead of from obj below
            obj = find_object_by_obj_ref_func(objref) # do not fetch any properties from this obj as we do not want to trigger more grpc calls

            if path in objects.keys():
                # duplicate paths!
                existing = objects[path]
                # create or append to a list of petrel objects
                if isinstance(existing, list):
                    existing.append(obj)
                else:
                    objects[path] = [existing, obj]
            else:
                # unique path
                objects[path] = obj
        return objects

    def __getitem__(self, key):
        try:
            return self._objects[key]   
        except KeyError:
            self._objects = self._query_objects(self._petrelconnection)
            return self._objects[key] 

    def __setitem__(self, key, value):
        raise Exception("This collection is read-only")

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        # This is not dict-like behaviour!
        return iter(self._objects.values())

    def keys(self):
        """The paths of the Petrel objects

        Returns:
            A list of the paths of the Petrel objects
        """
        return self._objects.keys()

    def values(self):
        """The Petrel objects

        Returns:
            A list of the Petrel objects"""
        return self._objects.values()

    def items(self):
        """The (`path`, `Petrel object`) pairs available.  If multiple objects
        have the same path, a list of Petrel objects is returned.

        Returns:
            A list of (`path`, `objects`) tuples (pairs) available

        """
        return self._objects.items()

    def __str__(self):
        return str(self._objects)

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)})"

class Properties(PetrelObjectStoreBase):
    """A read-only collection of GridProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grid_properties(),
            lambda guid: petrelconnection._get_grid_property_by_guid(guid)
        )

class DiscreteProperties(PetrelObjectStoreBase):
    """A read-only collection of GridDiscreteProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grid_properties(discrete = True),
            lambda guid: petrelconnection._get_grid_property_by_guid(guid, discrete = True)
        )

class Grids(PetrelObjectStoreBase):
    """A read-only collection of Grid objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_grids(),
            lambda guid: petrelconnection._get_grid_by_guid(guid)
        )

class SeismicCubes(PetrelObjectStoreBase):
    """A read-only collection of Seismic Cube objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_seismic_cubes(),
            lambda guid: petrelconnection._get_seismic_cube_by_guid(guid)
        )

class HorizonProperties(PetrelObjectStoreBase):
    """A collection of HorizonProperty objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_properties(),
            lambda guid: petrelconnection._get_horizon_property_by_guid(guid)
        )

class PropertyCollections(PetrelObjectStoreBase):
    """A collection of PropertyCollection objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_property_collections(),
            lambda guid: petrelconnection._get_property_collection_by_guid(guid)
        )

class HorizonInterpretation3Ds(PetrelObjectStoreBase):
    """ A collection of HorizonInterpretation3D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_interpretation_3ds(),
            lambda guid: petrelconnection._get_horizon_interpretation_3d_by_guid(guid)
        )

class HorizonInterpretations(PetrelObjectStoreBase):
    """ A collection of HorizonInterpretation3D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_horizon_interpretations(),
            lambda guid: petrelconnection._get_horizon_interpretation_by_guid(guid)
        )

class Seismic2Ds(PetrelObjectStoreBase):
    """ A collection of Seismic2D objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_seismic_2ds(),
            lambda guid: petrelconnection._get_seismic_2d_by_guid(guid)
        )

class Surfaces(PetrelObjectStoreBase):
    """A read-only collection of Surface objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surfaces(),
            lambda guid: petrelconnection._get_surface_by_guid(guid)
        )

class SurfaceAttributes(PetrelObjectStoreBase):
    """A read-only collection of SurfaceAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surface_attributes(),
            lambda guid: petrelconnection._get_surface_attribute_by_guid(guid)
        )

class SurfaceDiscreteAttributes(PetrelObjectStoreBase):
    """A read-only collection of SurfaceDiscreteAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_surface_attributes(discrete = True),
            lambda guid: petrelconnection._get_surface_attribute_by_guid(guid, discrete = True)
        )

class WellLogs(PetrelObjectStoreBase):
    """A read-only collection of WellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_logs(),
            lambda guid: petrelconnection._get_well_log_by_guid(guid)
        )

class DiscreteWellLogs(PetrelObjectStoreBase):
    """A read-only collection of DiscreteWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_logs(discrete = True),
            lambda guid: petrelconnection._get_well_log_by_guid(guid, discrete = True)
        )

class GlobalWellLogs(PetrelObjectStoreBase):
    """A read-only collection GlobalWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_well_logs(), 
            lambda guid: petrelconnection._get_global_well_log_by_guid(guid)
        )

class GlobalObservedDataSets(PetrelObjectStoreBase):
    """A read-only collection GlobalObservedDataSet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_observed_data_sets(),
            lambda guid: petrelconnection._get_global_observed_data_set(guid)
        )

class DiscreteGlobalWellLogs(PetrelObjectStoreBase):
    """A read-only collection of DiscreteWellLog objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_global_well_logs(discrete = True),
            lambda guid: petrelconnection._get_global_well_log_by_guid(guid, discrete = True)
        )

class Wells(PetrelObjectStoreBase):
    """A read-only collection of Well objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_wells(),
            lambda guid: petrelconnection._get_well_by_guid(guid)
        )

class WellAttributes(PetrelObjectStoreBase):
    """A read-only collection of WellAttribute objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_attributes(),
            lambda guid: petrelconnection._get_well_attribute_by_guid(guid)
        )

class WellFolders(PetrelObjectStoreBase):
    """A read-only collection of WellFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_well_folders(),
            lambda guid: petrelconnection._get_well_folder_by_guid(guid)
        )

class MarkerCollections(PetrelObjectStoreBase):
    """A read-only collection of Marker Collection objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_markercollections(),
            lambda guid: petrelconnection._get_markercollection_by_guid(guid)
        )

class PointSets(PetrelObjectStoreBase):
    """A read-only collection of PointSet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_pointsets(),
            lambda guid: petrelconnection._get_pointset_by_guid(guid)
        )
    
class FaultInterpretations(PetrelObjectStoreBase):
    """A read-only collection of FaultInterpretation objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_fault_interpretations(),
            lambda guid: petrelconnection._get_fault_interpretation_by_guid(guid)
        )
    
class InterpretationFolders(PetrelObjectStoreBase):
    """A read-only collection of InterpretationFolder objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_interpretation_folders(),
            lambda guid: petrelconnection._get_interpretation_folder_by_guid(guid)
        )

class PolylineSets(PetrelObjectStoreBase):
    """A read-only collection of PolylineSets objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_polylinesets(),
            lambda guid: petrelconnection._get_polylineset_by_guid(guid)
        )

class Wavelets(PetrelObjectStoreBase):
    """A read-only collection of Wavelet objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_wavelets(),
            lambda guid: petrelconnection._get_wavelet_by_guid(guid)
        )

class Workflows(PetrelObjectStoreBase):
    """A read-only collection of Workflow objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_workflows(),
            lambda guid: petrelconnection._get_workflow_by_guid(guid)
        )

class ReferenceVariables(PetrelObjectStoreBase):
    """A read-only collection of ReferenceVariable objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_reference_variables(),
            lambda guid: petrelconnection._get_reference_variable_by_guid(guid)
        )

class WellSurveys(PetrelObjectStoreBase):
    """A read-only collection of WellSurvey objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_object_from_ref(
            petrelconnection._find_well_surveys(),
            lambda obj: petrelconnection._pb_PetrelObjectGuid_to_pyobj_wrapper(
                utils.pb_PetrelObjectRef_to_grpcobj(obj, petrelconnection)
            )
        )

class ObservedDataObjects(PetrelObjectStoreBase):
    """A read-only collection of ObservedData objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_observed_data(),
            lambda guid: petrelconnection._get_observed_data_by_guid(guid)
        )

class ObservedDataSets(PetrelObjectStoreBase):
    """A read-only collection of ObservedDataSets objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_observed_data_sets(),
            lambda guid: petrelconnection._get_observed_data_set_by_guid(guid)
        )

class Zones(PetrelObjectStoreBase):
    """A read-only collection of Zone objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_zones(),
            lambda guid: petrelconnection._get_zone_by_guid(guid)
        )

class Segments(PetrelObjectStoreBase):
    """A read-only collection of Segment objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_segments(),
            lambda guid: petrelconnection._get_segment_by_guid(guid)
        )

class Templates(PetrelObjectStoreBase):
    """A read-only collection of Template objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_templates(),
            lambda guid: petrelconnection._get_template_by_guid(guid)
        )

class DiscreteTemplates(PetrelObjectStoreBase):
    """A read-only collection of DiscreteTemplate objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_discrete_templates(),
            lambda guid: petrelconnection._get_discrete_template_by_guid(guid)
        )

class CheckShots(PetrelObjectStoreBase):
    """A read-only collection of CheckShot objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_checkshots(),
            lambda guid: petrelconnection._get_checkshot_by_guid(guid)
        )

class SavedSearches(PetrelObjectStoreBase):
    """A read-only collection of SavedSearch objects."""
    def _query_objects(self, petrelconnection):
        petrelconnection._opened_test()
        return self.get_petrel_objects(
            petrelconnection._find_saved_searches(),
            lambda guid: petrelconnection._get_saved_search_by_guid(guid)
        )