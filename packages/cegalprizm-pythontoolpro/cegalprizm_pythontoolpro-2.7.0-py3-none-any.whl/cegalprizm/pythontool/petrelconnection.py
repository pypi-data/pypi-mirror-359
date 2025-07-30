# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import grpc
import typing
import pandas as pd
import pkg_resources
import contextlib
from packaging import version
import numpy as np
from typing import List, Union

from warnings import warn
from enum import Enum
from cegalprizm.hub import BaseContext

from cegalprizm.pythontool import _utils
from cegalprizm.pythontool.grpc import utils, petrelinterface_pb2
from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, Primitives
from cegalprizm.pythontool.oophub.workflowvars_hub import WorkflowvarsHub
from cegalprizm.pythontool.ooponly.ptutils import Utils

from cegalprizm.pythontool.grpc.workflow_grpc import ReferenceVariableGrpc, WorkflowGrpc
from cegalprizm.pythontool.grpc.grid_grpc import GridGrpc
from cegalprizm.pythontool.grpc.gridproperty_grpc import GridPropertyGrpc, GridDiscretePropertyGrpc, PropertyCollectionGrpc
from cegalprizm.pythontool.grpc.surface_grpc import SurfaceGrpc, SurfacePropertyGrpc, SurfaceDiscretePropertyGrpc
from cegalprizm.pythontool.grpc.seismic_grpc import Seismic2DGrpc, SeismicCubeGrpc 
from cegalprizm.pythontool.grpc.borehole_grpc import BoreholeGrpc, WellLogGrpc, DiscreteWellLogGrpc, GlobalWellLogGrpc, DiscreteGlobalWellLogGrpc
from cegalprizm.pythontool.grpc.borehole_collection_grpc import BoreholeCollectionGrpc
from cegalprizm.pythontool.grpc.markercollection_grpc import MarkerCollectionGrpc
from cegalprizm.pythontool.grpc.points_grpc import PointSetGrpc, PropertyRangeHandler
from cegalprizm.pythontool.grpc.polylines_grpc import PolylineSetGrpc
from cegalprizm.pythontool.grpc.faultinterpretation_grpc import FaultInterpretationGrpc
from cegalprizm.pythontool.grpc.interpretation_collection_grpc import InterpretationCollectionGrpc
from cegalprizm.pythontool.grpc.wavelet_grpc import WaveletGrpc
from cegalprizm.pythontool.grpc.wellsurvey_grpc import XyzWellSurveyGrpc, XytvdWellSurveyGrpc, DxdytvdWellSurveyGrpc, MdinclazimWellSurveyGrpc, ExplicitWellSurveyGrpc
from cegalprizm.pythontool.grpc.horizoninterpretation_grpc import HorizonInterpretation3dGrpc, HorizonProperty3dGrpc, HorizonInterpretationGrpc
from cegalprizm.pythontool.grpc.observeddata_grpc import ObservedDataGrpc, ObservedDataSetGrpc, GlobalObservedDataSetsGrpc
from cegalprizm.pythontool.grpc.template_grpc import TemplateGrpc, DiscreteTemplateGrpc
from cegalprizm.pythontool.grpc.checkshot_grpc import CheckShotGrpc
from cegalprizm.pythontool.grpc.savedsearch_grpc import SavedSearchGrpc
from cegalprizm.pythontool.grpc.wellattribute_grpc import WellAttributeGrpc
from cegalprizm.pythontool.grpc.petrelobjects import Properties as PO_Properties
from cegalprizm.pythontool.grpc.petrelobjects import Grids as PO_Grids
from cegalprizm.pythontool.grpc.petrelobjects import SeismicCubes as PO_SeismicCubes
from cegalprizm.pythontool.grpc.petrelobjects import Seismic2Ds as PO_Seismic2Ds
from cegalprizm.pythontool.grpc.petrelobjects import Surfaces as PO_Surfaces
from cegalprizm.pythontool.grpc.petrelobjects import SurfaceAttributes as PO_SurfaceAttributes
from cegalprizm.pythontool.grpc.petrelobjects import DiscreteProperties as PO_DiscreteProperties
from cegalprizm.pythontool.grpc.petrelobjects import SurfaceDiscreteAttributes as PO_SurfaceDiscreteAttributes
from cegalprizm.pythontool.grpc.petrelobjects import WellLogs as PO_WellLogs
from cegalprizm.pythontool.grpc.petrelobjects import GlobalWellLogs as PO_GlobalWellLogs
from cegalprizm.pythontool.grpc.petrelobjects import DiscreteGlobalWellLogs as PO_DiscreteGlobalWellLogs
from cegalprizm.pythontool.grpc.petrelobjects import DiscreteWellLogs as PO_DiscreteWellLogs
from cegalprizm.pythontool.grpc.petrelobjects import PointSets as PO_PointSets
from cegalprizm.pythontool.grpc.petrelobjects import PolylineSets as PO_PolylineSets
from cegalprizm.pythontool.grpc.petrelobjects import FaultInterpretations as PO_FaultInterpretations
from cegalprizm.pythontool.grpc.petrelobjects import InterpretationFolders as PO_InterpretationFolders
from cegalprizm.pythontool.grpc.petrelobjects import Wells as PO_Wells
from cegalprizm.pythontool.grpc.petrelobjects import WellFolders as PO_WellFolders
from cegalprizm.pythontool.grpc.petrelobjects import MarkerCollections as PO_MarkerCollections
from cegalprizm.pythontool.grpc.petrelobjects import HorizonInterpretation3Ds as PO_HorizonInterpretation3Ds
from cegalprizm.pythontool.grpc.petrelobjects import HorizonInterpretations as  PO_HorizonInterpretations
from cegalprizm.pythontool.grpc.petrelobjects import HorizonProperties as PO_HorizonProperties
from cegalprizm.pythontool.grpc.petrelobjects import PropertyCollections as PO_PropertyCollections
from cegalprizm.pythontool.grpc.petrelobjects import Wavelets as PO_Wavelets
from cegalprizm.pythontool.grpc.petrelobjects import Workflows as PO_Workflows
from cegalprizm.pythontool.grpc.petrelobjects import WellSurveys as PO_WellSurveys
from cegalprizm.pythontool.grpc.petrelobjects import ObservedDataSets as PO_ObservedDataSets
from cegalprizm.pythontool.grpc.petrelobjects import GlobalObservedDataSets as PO_GlobalObservedDataSets
from cegalprizm.pythontool.grpc.petrelobjects import Templates as PO_Templates
from cegalprizm.pythontool.grpc.petrelobjects import DiscreteTemplates as PO_DiscreteTemplates
from cegalprizm.pythontool.grpc.petrelobjects import CheckShots as PO_CheckShots
from cegalprizm.pythontool.grpc.petrelobjects import SavedSearches as PO_SavedSearches
from cegalprizm.pythontool.grpc.petrelobjects import WellAttributes as PO_WellAttributes
from cegalprizm.pythontool.oophub.borehole_hub import BoreholeHub
from cegalprizm.pythontool.oophub.borehole_collection_hub import BoreholeCollectionHub
from cegalprizm.pythontool.oophub.completionsset_hub import CompletionsSetHub
from cegalprizm.pythontool.oophub.grid_hub import GridHub
from cegalprizm.pythontool.oophub.horizon_hub import HorizonHub, HorizonInterpretationHub
from cegalprizm.pythontool.oophub.gridproperty_hub import GridPropertyHub
from cegalprizm.pythontool.oophub.globalwelllog_hub import GlobalWellLogHub
from cegalprizm.pythontool.oophub.globalobserveddata_hub import GlobalObservedDataSetsHub
from cegalprizm.pythontool.oophub.markercollection_hub import MarkerCollectionHub
from cegalprizm.pythontool.oophub.petrelobject_hub import PetrelObjectHub
from cegalprizm.pythontool.oophub.project_hub import ProjectHub
from cegalprizm.pythontool.oophub.points_hub import PointsHub
from cegalprizm.pythontool.oophub.polylines_hub import PolylinesHub
from cegalprizm.pythontool.oophub.faultinterpretation_hub import FaultInterpretationHub
from cegalprizm.pythontool.oophub.interpretation_collection_hub import InterpretationCollectionHub
from cegalprizm.pythontool.oophub.observeddata_hub import ObservedDataHub, ObservedDataSetHub
from cegalprizm.pythontool.oophub.workflow_hub import ReferenceVariableHub, WorkflowHub
from cegalprizm.pythontool.oophub.seismic_hub import SeismicHub
from cegalprizm.pythontool.oophub.seismic2d_hub import Seismic2DHub
from cegalprizm.pythontool.oophub.surface_hub import SurfaceHub
from cegalprizm.pythontool.oophub.surfacecollection_hub import SurfaceCollectionHub
from cegalprizm.pythontool.oophub.surfaceproperty_hub import SurfacePropertyHub
from cegalprizm.pythontool.oophub.wavelet_hub import WaveletHub
from cegalprizm.pythontool.oophub.welllog_hub import WellLogHub
from cegalprizm.pythontool.oophub.wellsurvey_hub import XyzWellSurveyHub, XytvdWellSurveyHub, DxdytvdWellSurveyHub, MdinclazimWellSurveyHub, ExplicitWellSurveyHub 
from cegalprizm.pythontool.oophub.zone_hub import ZoneHub
from cegalprizm.pythontool.oophub.segment_hub import SegmentHub
from cegalprizm.pythontool.oophub.ptphubcontext import PtpHubContext
from cegalprizm.pythontool.oophub.template_hub import TemplateHub, DiscreteTemplateHub
from cegalprizm.pythontool.oophub.checkshot_hub import CheckShotHub
from cegalprizm.pythontool.oophub.savedsearch_hub import SavedSearchHub
from cegalprizm.pythontool.oophub.wellattribute_hub import WellAttributeHub
from cegalprizm.pythontool.grid import Grid
from cegalprizm.pythontool.gridproperty import GridProperty, GridDiscreteProperty, PropertyCollection
from cegalprizm.pythontool.surface import Surface, SurfaceAttribute, SurfaceDiscreteAttribute
from cegalprizm.pythontool.borehole import Well
from cegalprizm.pythontool.wellfolder import WellFolder
from cegalprizm.pythontool.wellsymboldescription import WellSymbolDescription
from cegalprizm.pythontool.template import Template, DiscreteTemplate
from cegalprizm.pythontool.checkshot import CheckShot
from cegalprizm.pythontool.welllog import WellLog, DiscreteWellLog, GlobalWellLog, DiscreteGlobalWellLog
from cegalprizm.pythontool.markercollection import MarkerCollection
from cegalprizm.pythontool.points import PointSet
from cegalprizm.pythontool.polylines import PolylineSet
from cegalprizm.pythontool.faultinterpretation import FaultInterpretation
from cegalprizm.pythontool.interpretationfolder import InterpretationFolder
from cegalprizm.pythontool.horizoninterpretation import HorizonInterpretation3d, HorizonProperty3d, HorizonInterpretation
from cegalprizm.pythontool.savedsearch import SavedSearch
from cegalprizm.pythontool.seismic import SeismicCube, SeismicLine
from cegalprizm.pythontool.wavelet import Wavelet
from cegalprizm.pythontool.wellsurvey import WellSurvey
from cegalprizm.pythontool.workflow import ReferenceVariable, Workflow, _pb_grpcobj_to_pyobj
from cegalprizm.pythontool.observeddata import ObservedData, ObservedDataSet, GlobalObservedDataSet
from cegalprizm.pythontool.experimental import set_experimental_ok, experimental_method, experimental_property
from cegalprizm.pythontool.exceptions import PythonToolException
from cegalprizm.pythontool.workflowvars import WorkflowVars
from cegalprizm.pythontool.wellattribute import WellAttribute, WellAttributeFilterEnum, WellAttributeType

@contextlib.contextmanager
def make_connection(
         allow_experimental: typing.Optional[bool] = None, 
         enable_history: typing.Optional[bool] = True, 
         petrel_ctx: typing.Optional["BaseContext"] = None)\
        -> typing.Iterator["PetrelConnection"]:
    """A context-manager that provides a connection to Petrel.  A typical usage is 

    with make_connection() as p:
        p.wells
        ...
    
    The connection is closed automatically when the `with` context is exited.  

    See `cegalprizm.pythontool.petrelconnection.PetrelConnection` for more details.
    """
    c =  PetrelConnection(allow_experimental, enable_history, petrel_ctx)
    try:
        c.open()
        yield c
    finally:
        c.close()

def _get_version():
    return pkg_resources.get_distribution('cegalprizm-pythontoolpro').version

class PetrelConnectionState(Enum):
    UNOPENED = 1
    OPENED = 2
    CLOSED = 3

class PetrelConnection:
    """Creates a connection to Petrel*. A typical usage is

    .. code-block:: Python

        ptp = PetrelConnection()
        '''write some code accessing Petrel here'''
        ptp.close()

    Python Tool Pro will try to connect to a running Hub server and will create a default Petrel context (petrel_ctx). This will work if 1 Petrel connector (1 Petrel instance) is connected to the Hub server. If multiple Petrel connectors are available you need to define the Petrel context to ensure you connect to the correct Petrel instance.

    Args:
        petrel_ctx: A context or handle to a Cegal Hub Petrel Connector
        allow_experimental: Enable experimental methods to be called. Defaults to False
        enable_history: Petrel data object history is updated when changed from Python Tool Pro. Defaults to True.

    Petrel* is a mark of SLB.
    """

    def __init__(self, allow_experimental: typing.Optional[bool] = None, enable_history: typing.Optional[bool] = True, petrel_ctx: typing.Optional["BaseContext"] = None):
        self._preferred_streamed_unit_bytes: int = 2 * 1024 * 1024
        self._ptp_hub_ctx = PtpHubContext(petrel_ctx)
        from cegalprizm.hub import server_service_pb2

        try:
            self._ptp_hub_ctx.channel.server_request_stub.VerifyHealth(server_service_pb2.HealthQuery())
        except grpc._channel._InactiveRpcError as ine:
            message = ine.details()
            if (ine.code() is grpc.StatusCode.UNAVAILABLE):
                message += """\n\nPlease check if a Hub Server is running and available for connections. \
This information can be found in Cegal Hub Server Connection in the Cegal Hub plug-in in Marina in Petrel. \
For local connections; start a local Hub Server. For remote connections; please contact the Hub admin in your organisation.""" 
            if (ine.code() is grpc.StatusCode.UNKNOWN):
                message = """\n\nAuthentication failed because your account does not have the required Python Tool Pro license.
Please contact your Keystone tenant admin and request access to the license.
After the license has been added to your account by the tenant-admin, please run Verify License located under Cegal Python Tool Pro in the Marina plugin.
If you are unsure who your tenant admin is, log in to the Keystone portal at https://keystone.cegal-geo.com and click the Show My Admins button for assistance."""
            raise PythonToolException(message)
        except Exception as e:
            if "Time out waiting for login" in str(e):
                raise PythonToolException(str(e))
            message = "Please check if you have the correct access rights and that Petrel is opened with a Hub Server running available for connections."
            raise PythonToolException(message)
        
        self._service_project: ProjectHub = ProjectHub(self._ptp_hub_ctx)

        qcp = self._ptp_hub_ctx.channel.server_request_stub.QueryConnectors(server_service_pb2.ConnectorQuery()).available_connectors
        if len(qcp) == 0 or not any('cegal.hub.petrel' in c.wellknown_identifier for c in qcp):
            raise PythonToolException("Please check if Petrel is opened with a Hub Server running available for connections.")
        if not any('cegal.pythontool.Ping' in c.supported_payloads for c in qcp):
            raise PythonToolException("Please check if Python Tool Pro is installed and enabled in Petrel. If not, please contact your administrator.")
        # Test connection
        self._opened = PetrelConnectionState.UNOPENED
        try:
            self.ping()
            self._opened = PetrelConnectionState.OPENED
        except Exception as e:
            message = str(e)
            if "not authorized" in str(e):
                message = """\n\nAuthentication failed because your account does not have the required Python Tool Pro license.
Please contact your Keystone tenant admin and request access to the license. 
After the license has been added to your account by the tenant-admin, please run Verify License located under Cegal Python Tool Pro in the Marina plugin.
If you are unsure who your tenant admin is, log in to the Keystone portal at https://keystone.cegal-geo.com and click the Show My Admins button for assistance."""
            # if connection failed it could be because auth failed so delete possibly-invalid cached refresh_token
            raise PythonToolException(message)

        # Find if client version is accepted by server
        client_version_accepted, client_version, server_version = self._verify_version()
        if not client_version_accepted:
            raise PythonToolException(f'Python Tool Pro python package version {client_version} is not accepted by PTP Petrel plugin. Plugin version is {server_version}. Update python package and/or Petrel plugin to ensure compatibility.')

        # Common settings
        self._array_transfer_mode = petrelinterface_pb2.STREAM
        self._report = ''
        self._was_success = None
        self._enable_history = enable_history
        if allow_experimental is not None:
            set_experimental_ok(allow_experimental)
        self._set_enable_history(self._enable_history)

        # If we did not specify a petrel context we set the connector filter to ensure we always call the same petrel instance
        if petrel_ctx is None:
            self._set_connector_filter()

        self._service_petrel_object = PetrelObjectHub(self._ptp_hub_ctx) # type: ignore
        self._service_grid = GridHub(self._ptp_hub_ctx) # type: ignore
        self._service_grid_property = GridPropertyHub(self._ptp_hub_ctx) # type: ignore
        self._service_surface = SurfaceHub(self._ptp_hub_ctx) # type: ignore
        self._service_surface_property = SurfacePropertyHub(self._ptp_hub_ctx) # type: ignore
        self._service_surface_collection = SurfaceCollectionHub(self._ptp_hub_ctx) # type: ignore
        self._service_completionsset = CompletionsSetHub(self._ptp_hub_ctx) # type: ignore
        self._service_borehole = BoreholeHub(self._ptp_hub_ctx) # type: ignore
        self._service_boreholecollection = BoreholeCollectionHub(self._ptp_hub_ctx) # type: ignore
        self._service_markercollection = MarkerCollectionHub(self._ptp_hub_ctx) # type: ignore
        self._service_globalwelllog = GlobalWellLogHub(self._ptp_hub_ctx) # type: ignore
        self._service_globalobserveddatasets = GlobalObservedDataSetsHub(self._ptp_hub_ctx) # type: ignore
        self._service_welllog = WellLogHub(self._ptp_hub_ctx) # type: ignore
        self._service_seismic = SeismicHub(self._ptp_hub_ctx) # type: ignore
        self._service_seismic_2d = Seismic2DHub(self._ptp_hub_ctx) # type: ignore
        self._service_points = PointsHub(self._ptp_hub_ctx) # type: ignore
        self._service_polylines = PolylinesHub(self._ptp_hub_ctx) # type: ignore
        self._service_faultinterpretation = FaultInterpretationHub(self._ptp_hub_ctx) # type: ignore
        self._service_interpretationcollection = InterpretationCollectionHub(self._ptp_hub_ctx) # type: ignore
        self._service_horizon = HorizonHub(self._ptp_hub_ctx) # type: ignore
        self._service_wavelet = WaveletHub(self._ptp_hub_ctx) # type: ignore
        self._service_xyz_well_survey = XyzWellSurveyHub(self._ptp_hub_ctx) # type: ignore
        self._service_xytvd_well_survey = XytvdWellSurveyHub(self._ptp_hub_ctx) # type: ignore
        self._service_dxdytvd_well_survey = DxdytvdWellSurveyHub(self._ptp_hub_ctx) # type: ignore
        self._service_mdinclazim_well_survey = MdinclazimWellSurveyHub(self._ptp_hub_ctx) # type: ignore
        self._service_explicit_well_survey = ExplicitWellSurveyHub(self._ptp_hub_ctx) # type: ignore
        self._service_horizon_interpretation = HorizonInterpretationHub(self._ptp_hub_ctx) # type: ignore
        self._service_workflow = WorkflowHub(self._ptp_hub_ctx) # type: ignore
        self._service_referencevariable = ReferenceVariableHub(self._ptp_hub_ctx) # type: ignore
        self._service_observeddata = ObservedDataHub(self._ptp_hub_ctx) # type: ignore
        self._service_observeddataset = ObservedDataSetHub(self._ptp_hub_ctx) # type: ignore
        self._service_zone = ZoneHub(self._ptp_hub_ctx) # type: ignore
        self._service_segment = SegmentHub(self._ptp_hub_ctx) # type: ignore
        self._service_template = TemplateHub(self._ptp_hub_ctx) # type: ignore
        self._service_discrete_template = DiscreteTemplateHub(self._ptp_hub_ctx) # type: ignore
        self._service_checkshot = CheckShotHub(self._ptp_hub_ctx) # type: ignore
        self._service_savedsearch = SavedSearchHub(self._ptp_hub_ctx) # type: ignore
        self._service_wellattribute = WellAttributeHub(self._ptp_hub_ctx) # type: ignore

    def _set_connector_filter(self):
        from cegalprizm.hub import Hub, ConnectorFilter
        hub = Hub()
        qcp = hub.query_connectors("cegal.hub.petrel")
        conn_id = ""
        start_time = None
        if len(qcp) > 0:
            start_time = qcp[0].connect_date.seconds
            conn_id = qcp[0].connector_id
            # Usually (but not always) the first connector is the first one started
            # We compare with the connect date to make sure we always return the latest one
            for connector in qcp:
                if connector.connect_date.seconds > start_time:
                    start_time = connector.connect_date.seconds
                    conn_id = connector.connector_id
        if len(conn_id) > 0:
            connector_filter = ConnectorFilter(target_connector_id=conn_id)
            self._ptp_hub_ctx._set_connector_filter(connector_filter)


    def open(self) -> None:
        """DeprecationWarning: "petrelconnection.open() is deprecated and will 
           be removed in Python Tool Pro in 3.0. open() is no longer necessary
           after creating a new PetrelConnection object.
        """
        warn("petrelconnection.open() is deprecated and will be removed for Python \
             Tool Pro in 3.0. open() is no longer necessary after creating a new \
             PetrelConnection object.", 
             DeprecationWarning, stacklevel=2)
        pass

    def close(self) -> None:
        """Close the connection to Petrel.
        """
        self._opened = PetrelConnectionState.CLOSED
        self._ptp_hub_ctx.close()


    def __repr__(self) -> str:
        try:
            package_version = self._package_version
        except Exception:
            package_version = None

        try:
            opened = self._opened == PetrelConnectionState.OPENED
        except Exception:
            opened = None
        
        return 'PetrelConnection(package_version="{0}", opened="{1}")'.format(package_version, opened)

    def __str__(self) -> str:
        return self.__repr__()
    
    def _set_report(self, report):
        self._report = report.message
        self._was_success = report.value

    def _verify_version(self):
        # parse the version to a Version object to avoid using client_version with a possible 'rc' string in it. 
        client_version = version.parse(self._package_version)
        reply = self._service_project.GetServerVersion(petrelinterface_pb2.EmptyRequest())
        server_version = version.parse(reply.value)
        version_ok = client_version.major == server_version.major and client_version.minor == server_version.minor
        client_version_str = "{0}.{1}.{2}".format(client_version.major, client_version.minor, client_version.micro)
        server_version_str = "{0}.{1}.{2}".format(server_version.major, server_version.minor, server_version.micro)
        return version_ok, client_version_str, server_version_str

    def _set_enable_history(self, enable):
        request = petrelinterface_pb2.ProtoBool(value=enable)
        reply = self._service_project.EnableHistory(request)
        return reply.value

    def import_workflows(self, projectPath: str, workflowNames: typing.List[str]) -> typing.List[Workflow]:
        """Import a Petrel workflow from a different Petrel project.

        Args:
           projectPath: the file path to the Petrel project
           workflowNames: the Petrel name[s] of the workflow[s] to be imported
        """
        request = petrelinterface_pb2.Project_ImportWorkflow_Request(
            projectPath = projectPath
            , workflowNames = [v for v in workflowNames]
        )

        response = self._service_project.Project_ImportWorkflow(request)
             
        return [Workflow(WorkflowGrpc(item.guid, self)) for item in response.guids]

    @property
    def _package_version(self):
        return _get_version()
    
    def ping(self) -> int:
        """Typically used to verify connection to the server.

        Returns:
            int: A counter returned by the server
        """
        request = petrelinterface_pb2.EmptyRequest()
        reply = self._service_project.Ping(request)
        return reply.value 

    def a_project_is_active(self) -> bool:
        """Verify that a project is active on the server. A project must be active.

        Returns:
            bool: True if and only if a project is active
        """
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        reply = self._service_project.AProjectIsActive(request)
        return reply.value 
    
    @property
    def workflow_vars(self) -> "WorkflowVars":
        """The workflow variables of a Petrel workflow. These are the dollar sign variable users can define in a Petrel workflow. They can be of type double (numeric expression), sting (string expression), or date (date expression).
        
        **Note**:

        This property is only available if the PetrelConnection is established as part of a Cegal Prizm workflow executed within a Petrel workflow.
        
        
        **Example**:

        Set the value of a workflow variable of type string.

        .. code-block:: python

            ptp.workflow_vars[$string]='new string'

        **Example**:

        Set the value of a workflow variable of type double (numeric expression).

        .. code-block:: python

            ptp.workflow_vars[$numeric_expression]=5.4

        **Example**:

        Set the value of a workflow variable of type date (date expression). You need to import the Python library datetime for this.

        .. code-block:: python

            import datetime
            new_date=datetime.datetime(year=2023,month=10,day=30)
            ptp.workflow_vars[$date_expression]=new_date
        """
        return WorkflowVars(WorkflowvarsHub(self._ptp_hub_ctx))

    @property
    @_utils.crs_wkt_decorator(object_type="Project")
    def crs_wkt(self) -> str:
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        reply = self._service_project.GetCrs(request)
        return reply.value

    def get_current_project_name(self) -> str:
        """Returns the name of the Petrel project of the established connection."""
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        reply = self._service_project.GetCurrentProjectName(request)
        return reply.value

    def get_current_project_path(self) -> str:
        """Returns the path of the Petrel project of the established connection."""
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        reply = self._service_project.GetCurrentProjectPath(request)
        return reply.value

    def get_petrelobjects_by_guids(self, guids: typing.List[str]) -> typing.List[object]:
        """Get the Petrel objects with the given GUIDs

        Note:
            The GUIDs can be of the format listed below:
            1. 32-character hexadecimal string without dashes, e.g '1234567a123b567c123d567812345def'
            2. 32-character hexadecimal string including dashes, e.g '1234567a-123b-567c-123d-567812345def'
            3. 32-character hexadecimal string including dashes in braces, e.g '{1234567a-123b-567c-123d-567812345def}'
            4. 32-character hexadecimal string including dashes in parentheses, e.g '(1234567a-123b-567c-123d-567812345def)'
        
        Args:
            guids: A list of GUIDs as strings of the objects to be returned

        Returns: 
            A list with the objects for the given GUIDs. 
              If GUID  does not exist in Petrel project 'None' is returned.
        """
        self._opened_test()
        if (not isinstance(guids, list) or not all(isinstance(item, str) for item in guids)):
            raise PythonToolException("Input argument 'GUIDs' must be a list and all items must be string")
        invalid_guids = [guid for guid in guids if not _utils.is_valid_guid(guid)]
        if invalid_guids:
            raise ValueError(f"Invalid GUID format(s): {', '.join(invalid_guids)}")
        request = petrelinterface_pb2.ProtoStrings(values = [g for g in guids])
        responses = self._service_project.Project_GetPetrelObjectsByGuids(request)
        return [_pb_grpcobj_to_pyobj(utils.pb_PetrelObjectRef_to_grpcobj(item, self)) for item in responses]

    def get_petrel_project_units(self) -> typing.Dict[str, str]:
        """Get the Petrel project settings for coordinates and units.

        Returns: 
            A dictionary with the coordinates and units settings for the Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        response = self._service_project.Project_GetPetrelProjectUnits(request)
        return Utils.protobuf_map_to_dict(response.string_to_string_map)

    def append_scriptname_to_history(self, path_to_append: str) -> str:
        """Define path that will be appended to the history entries when objects are modified. 
        
        Args:
            path_to_append: The string of the path to append. 
        
        Example:

        from cegalprizm.pythontool.petrelconnection import PetrelConnection, make_connection
        petrel = PetrelConnection(allow_experimental=True)
        petrel.append_script_name_to_history('c:\\notebooks\\mergeworkbook.ipynb')
        #Modify
        petrel.close()

        """
        self._opened_test()
        request = petrelinterface_pb2.ProtoString(value=path_to_append)
        reply = self._service_project.SetScriptName(request)
        return reply.value 
    
    def create_fault_interpretation(self, name: str, domain: str, interpretation_folder: "InterpretationFolder") -> "FaultInterpretation":
        """Create a new fault interpretation in the specified interpretation folder.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created fault interpretation.
        
        Args:
            name (str): The name of the new fault interpretation as a string.
            domain (str): The domain of the new fault interpretation. The only valid inputs are 'Elevation time' or 'Elevation depth'.
            interpretation_folder (InterpretationFolder): The InterpretationFolder the new fault interpretation should be added to as a :class:`InterpretationFolder` object.

        Returns:
            FaultInterpretation: The new fault interpretation as a :class:`FaultInterpretation` object.
        
        Raises:
            ValueError: If the interpretation_folder argument is not a :class:`InterpretationFolder` object.
            ValueError: If the domain argument is not 'Elevation time' or 'Elevation depth'.

        **Example**:

        Create a new fault interpretation in the Input/Interpretations/Other Interpretations folder.

        .. code-block:: python

            interpretation_folder = petrel.interpretation_folders["Input/Interpretations/Other Interpretations"]
            new_fault_interpretation = petrel.create_fault_interpretation('New Interpretation', 'Elevation time', interpretation_folder)


        **Example**:

        Create a new fault interpretation using the domain from an existing fault interpretation.

        .. code-block:: python

            interpretation_folder = petrel.interpretation_folders["Input/Interpretations/Other Interpretations"]
            existing_fault_interpretation = petrel.fault_interpretations["Path/To/Existing_Fault_Interpretation"]
            new_fault_interpretation = petrel.create_fault_interpretation('New Interpretation', existing_fault_interpretation.domain, interpretation_folder)
        """
    
        self._opened_test()
        if not isinstance(interpretation_folder, InterpretationFolder):
            raise ValueError("interpretation_folder must be an InterpretationFolder object")
        if domain.lower() == "elevation time":
            domain_type = petrelinterface_pb2.DomainType.TIME
        elif domain.lower() == "elevation depth":           
            domain_type = petrelinterface_pb2.DomainType.DEPTH
        else:
            raise ValueError("domain must be 'Elevation time' or 'Elevation depth'")
        
        request = petrelinterface_pb2.CreateFaultInterpretation_Request(
            FaultInterpretationName = name,
            Domain = domain_type,
            InterpretationCollectionGuid = petrelinterface_pb2.PetrelObjectGuid(
                guid = interpretation_folder._interpretation_collection_object_link._guid,
                sub_type = interpretation_folder._interpretation_collection_object_link._sub_type,
            )
        )

        reply = self._service_faultinterpretation.CreateFaultInterpretation(request)
        if reply.guid:
            petrel_object_link = FaultInterpretationGrpc(reply.guid, self)
            return FaultInterpretation(petrel_object_link)
        else:
            return None

    def create_surface(self, name: str, domain: str, folder: InterpretationFolder, origin_corner: typing.Tuple[int, int], i_corner: typing.Tuple[int, int], j_corner: typing.Tuple[int, int], array: np.ndarray) -> Surface:
        """Create a new surface in the specified interpretation folder.
        
        Args:
            name (str): The name of the new Surface as a string.
            domain (str): The domain of the Surface, which must be 'Elevation depth' or 'Elevation time'.
            folder (`InterpretationFolder`): The interpretation folder to add the new Surface to.
            origin_corner (typing.Tuple[int, int]): The (x, y) coordinates of the origin corner of the Surface grid.
            i_corner (typing.Tuple[int, int]): The (x, y) coordinates of the i-direction corner of the Surface grid, indicating the extent of the grid in the i-direction. Must be orthogonal to the line formed between origin_corner and j_corner.
            j_corner (typing.Tuple[int, int]): The (x, y) coordinates of the j-direction corner of the Surface grid, indicating the extent of the grid in the j-direction. Must be orthogonal to the line formed between origin_corner and i_corner.
            array (np.ndarray): A numpy array containing the elevation data or time data of the Surface grid, depending on the domain.

        Returns:
            Surface: The new Surface as a :class:`Surface` object.

        Raises:
            ValueError: If the array argument is not a numpy array.
            ValueError: If the array argument is not a 2D numpy array.
            ValueError: If the domain argument is not 'Elevation time' or 'Elevation depth'.
            ValueError: If the folder argument is not a :class:`InterpretationFolder` object.

        **Example**:

        Create a new surface.

        .. code-block:: python

            petrel = PetrelConnection()
            xmin = 500000.0	
            xmax = 520000.0
            ymin = 6000000.0	
            ymax = 6200000.0
            p0 = (xmin, ymin)
            p1 = (xmax, ymin)
            p2 = (xmin, ymax)
            name = "a_surface"
            folder = next(iter(petrel.interpretation_folders.values()))
            domain = "Elevation depth"
            arr = np.random.rand(100, 100)
            surface = petrel.create_surface(name, domain, folder, p0, p1, p2 , arr)
        """
        if not isinstance(array, np.ndarray):
            raise ValueError("array must be a numpy array")
        if array.ndim != 2:
            raise ValueError("array must be a 2D numpy array")
        
        if domain.lower() == "elevation time":
            domain_type = petrelinterface_pb2.DomainType.TIME
        elif domain.lower() == "elevation depth":           
            domain_type = petrelinterface_pb2.DomainType.DEPTH
        else:
            raise ValueError("domain must be 'Elevation time' or 'Elevation depth'")
        if (origin_corner[0] == i_corner[0] and origin_corner[1] == i_corner[1]) or (origin_corner[0] == j_corner[0] and origin_corner[1] == j_corner[1]) or (i_corner[0] == j_corner[0] and i_corner[1] == j_corner[1]):
            raise ValueError("origin_corner, i_corner and j_corner must not be the same point")
        
        self._opened_test()
        if isinstance(folder, InterpretationFolder):
            folder_guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = folder._interpretation_collection_object_link._guid,
                sub_type = folder._interpretation_collection_object_link._sub_type
            )
        else:
            raise ValueError("Unsupported folder type")
        
        def chunks(lst, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        flattened_array = [0]*array.size
        for j in range(array.shape[1]):
            for i in range(array.shape[0]):
                flattened_array[j*array.shape[0]+i] = array[i,j]

        requests = ( 
            petrelinterface_pb2.CreateSurface_Request(
                SurfaceName = name,
                SurfaceCollectionGuid = folder_guid,
                SizeI = array.shape[0],
                SizeJ = array.shape[1],
                OriginCorner = petrelinterface_pb2.Primitives.Double2(x = origin_corner[0], y = origin_corner[1]),
                ICorner = petrelinterface_pb2.Primitives.Double2(x = i_corner[0], y = i_corner[1]),
                JCorner = petrelinterface_pb2.Primitives.Double2(x = j_corner[0], y = j_corner[1]),
                Domain = domain_type,
                Samples = chunk) 
            for chunk in chunks(flattened_array, 1024))

        reply = self._service_surface.CreateSurface(requests)
        if reply.guid:
            petrel_object_link = SurfaceGrpc(reply.guid, self)
            return Surface(petrel_object_link)
        else:
            return None
    
    def create_well(self, well_name: str, well_folder: "WellFolder") -> "Well":
        """Create a new Well object in the specified WellFolder. 
        After creation the wellhead coordinates, working reference level and well survey (trajectory) should be set to avoid an incomplete state.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created well.
        
        Args:
            well_name (str): The name of the new well as a string.
            well_folder (WellFolder): The WellFolder the new well should be added to as a :class:`WellFolder` object.

        Returns:
            Well: The new well as a :class:`Well` object.

        Raises:
            ValueError: If the well_folder argument is not a :class:`WellFolder` object.

        **Example**:

        Create a new well in the Input/Wells/Other Wells folder and set required properties.

        .. code-block:: python

            well_folder = petrel.well_folders["Input/Wells/Other Wells"]
            new_well = petrel.create_well('New Well', well_folder)
            coordinates = (458003.1334, 6785817.93)
            ref_level = ("RKB", 23.4, "Rotary Kelly Bushing")
            new_well.wellhead_coordinates = coordinates
            new_well.well_datum = ref_level
            new_survey = new_well.create_well_survey("BasicSurvey", "DX DY TVD survey")
            new_survey.set(dxs=[0,0], dys=[0,0], tvds=[0,1500])

        **Example**:

        Create a new well in the Input/Wells/Other Wells folder and copy properties from another well.

        .. code-block:: python

            old_well = petrel.wells["Path/To/Old_Well"]
            well_folder = petrel.well_folders["Input/Wells/Other Wells"]
            new_well = petrel.create_well('Well Copy', well_folder)
            new_well.wellhead_coordinates = old_well.wellhead_coordinates
            new_well.well_datum = old_well.well_datum
            new_survey = new_well.create_well_survey("XYZ", "X Y Z survey")
            survey_df = old_well.surveys[0].as_dataframe()
            x_vals = list(survey_df["X"])
            y_vals = list(survey_df["Y"])
            z_vals = list(survey_df["Z"])
            new_survey.set(xs=x_vals, ys=y_vals, zs=z_vals)
        """
        self._opened_test()
        if not isinstance(well_folder, WellFolder):
            raise ValueError("well_folder must be a WellFolder object")
        request = petrelinterface_pb2.PetrelObjectGuidAndString(
            guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = well_folder._borehole_collection_object_link._guid,
                sub_type = well_folder._borehole_collection_object_link._sub_type),
            value = well_name
        )
        reply = self._service_borehole.CreateBorehole(request)
        if reply.guid:
            petrel_object_link = BoreholeGrpc(reply.guid, self)
            new_well = Well(petrel_object_link)
            new_well.readonly = False
            return new_well
        else:
            return None
        
    def create_polylineset(self, name: str, folder = None, template: Template = None) -> PolylineSet:
        """Create a new PolylineSet object.
        Use the optional folder argument to specify a folder to add the new PolylineSet to. By default the PolylineSet is added to the root folder. Currently only InterpretationFolders are supported.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created PolylineSet.

        Args:
            name (str): The name of the new PolylineSet as a string.
            folder (optional): The folder to add the new PolylineSet to. Defaults to None (PolylineSet added to project root).
            template (optional): The template to use for the new PolylineSet as a :class:`Template` object. With the default (None) input, Elevation depth will be used.

        Returns:
            PolylineSet: The new PolylineSet as a :class:`PolylineSet` object.

        Raises:
            ValueError: If the folder argument is not a :class:`InterpretationFolder` object.
            ValueError: If the template argument is not a :class:`Template` object. DiscreteTemplate is not supported.

        **Example**:

        Create a new polylineset in the root folder.

        .. code-block:: python

            new_polylineset = petrel.create_polylineset('New Polyline')
            
        **Example**:

        Create a new polylineset in an interpretation folder and use a specific template.

        .. code-block:: python

            folder = petrel.interpretation_folders["Input/Interpretations/Other Interpretations"]
            template = petrel.templates["Path/To/Template"]
            new_polylineset = petrel.create_polylineset('New Polyline', folder, template)
        """
        self._opened_test()
        if folder is None:
            folder_type = petrelinterface_pb2.FolderType.ProjectRoot
            folder_guid = petrelinterface_pb2.PetrelObjectGuid()
        else:
            if isinstance(folder, InterpretationFolder):
                folder_type = petrelinterface_pb2.FolderType.InterpretationFolder
                folder_guid = petrelinterface_pb2.PetrelObjectGuid(
                    guid = folder._interpretation_collection_object_link._guid,
                    sub_type = folder._interpretation_collection_object_link._sub_type
                )
            else:
                raise ValueError("Unsupported folder type")

        template_guid = petrelinterface_pb2.PetrelObjectGuid()
        if template is not None:
            if not isinstance(template, Template):
                raise ValueError("template must be a Template object. DiscreteTemplate is not supported.")
            template_guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = template._petrel_object_link._guid,
                sub_type = template._petrel_object_link._sub_type
            )
            
        request = petrelinterface_pb2.CreatePolylineSet_Request(
            Name = name,
            FolderType = folder_type,
            FolderGuid = folder_guid,
            TemplateGuid = template_guid
        )

        reply = self._service_polylines.CreatePolylineSet(request)
        if reply.guid:
            petrel_object_link = PolylineSetGrpc(reply.guid, self)
            return PolylineSet(petrel_object_link)
        else:
            return None
        
    def create_pointset(self, name: str, folder = None, template: Template = None) -> PointSet:
        """Create a new PointSet object.
        Use the optional folder argument to specify a folder to add the new PointSet to. By default the PointSet is added to the root folder. Currently only InterpretationFolders are supported.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created PointSet.

        Args:
            name (str): The name of the new PointSet as a string.
            folder (optional): The folder to add the new PointSet to. Defaults to None (PointSet added to project root).
            template (optional): The template to use for the new PointSet as a :class:`Template` object. With the default (None) input, Elevation depth will be used.

        Returns:
            PointSet: The new PointSet as a :class:`PointSet` object.

        Raises:
            ValueError: If the folder argument is not a :class:`InterpretationFolder` object.
            ValueError: If the template argument is not a :class:`Template` object. DiscreteTemplate is not supported.

        **Example**:

        Create a new pointset in the root folder.

        .. code-block:: python

            new_pointset = petrel.create_pointset('New Pointset')
            
        **Example**:

        Create a new pointset in an interpretation folder and use a specific template.

        .. code-block:: python

            folder = petrel.interpretation_folders["Input/Interpretations/Other Interpretations"]
            template = petrel.templates["Path/To/Template"]
            new_pointset = petrel.create_pointset('New Pointset', folder, template)
        """
        self._opened_test()
        if folder is None:
            folder_type = petrelinterface_pb2.FolderType.ProjectRoot
            folder_guid = petrelinterface_pb2.PetrelObjectGuid()
        else:
            if isinstance(folder, InterpretationFolder):
                folder_type = petrelinterface_pb2.FolderType.InterpretationFolder
                folder_guid = petrelinterface_pb2.PetrelObjectGuid(
                    guid = folder._interpretation_collection_object_link._guid,
                    sub_type = folder._interpretation_collection_object_link._sub_type
                )
            else:
                raise ValueError("Unsupported folder type")

        template_guid = petrelinterface_pb2.PetrelObjectGuid()
        if template is not None:
            if not isinstance(template, Template):
                raise ValueError("template must be a Template object. DiscreteTemplate is not supported.")
            template_guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = template._petrel_object_link._guid,
                sub_type = template._petrel_object_link._sub_type
            )
        
        request = petrelinterface_pb2.CreatePointSet_Request(
            Name = name,
            FolderType = folder_type,
            FolderGuid = folder_guid,
            TemplateGuid = template_guid
        )

        reply = self._service_points.CreatePointSet(request)
        if reply.guid:
            petrel_object_link = PointSetGrpc(reply.guid, self)
            return PointSet(petrel_object_link)
        else:
            return None

    def create_well_attribute(self, name: str, attribute_type: typing.Union[WellAttributeType, str], template: Template = None):
        """Create a new well attribute of the specified type.
        Use the optional template argument to specify a template to use for the new well attribute. Template is only supported when creating 'discrete' or 'continuous' well attributes.
        Note that if an empty string is passed as the name argument, Petrel will automatically assign a name to the created well attribute.

        Args:
            name (str): The name of the new well attribute as a string. If an empty string is passed, Petrel will automatically assign a name.
            attribute_type (Union[WellAttributeType, str]): The type of the new well attribute. Must be a :class:`WellAttributeType` or a string with the value 'continuous', 'discrete', 'string', 'boolean' or 'datetime'.
            template (optional): The template to use for the new well attribute as a :class:`Template` object for 'continuous' well attribute or :class:`DiscreteTemplate` for 'discrete' well attribute. With the default (None) input, default template is used.
        
        Raises:
            ValueError: If the attribute_type argument is not a :class:`WellAttributeType` or a string with the value 'continuous', 'discrete', 'string', 'boolean' or 'datetime'.
            ValueError: If the template argument is not a :class:`Template` object for 'continuous' well attribute or :class:`DiscreteTemplate` for 'discrete' well attribute.
            ValueError: If the template argument is not supported for the attribute type.
            TypeError: If the attribute_type argument is not a :class:`WellAttributeType` or a string.
            PythonToolException: If the creation of the well attribute fails.

        **Example**:

        Create a new well attribute for each type, with and without WellAttributeType and Template.

        .. code-block:: python

            from cegalprizm.pythontool import WellAttributeType
            discrete_template = petrel.discrete_templates["Templates/Discrete property templates/General discrete"]
            petrel.create_well_attribute('ContinuousAttribute', 'continuous')
            petrel.create_well_attribute('DiscreteAttribute', 'discrete', discrete_template)
            petrel.create_well_attribute('StringAttribute', WellAttributeType.String)
            petrel.create_well_attribute('BooleanAttribute', WellAttributeType.Boolean)
            petrel.create_well_attribute('DateTimeAttribute', 'datetime')
        """
        self._opened_test()
        all_enum_values = [e.value.lower() for e in WellAttributeType]
        if isinstance(attribute_type, WellAttributeType):
            attribute_type_str = attribute_type.value
        elif isinstance(attribute_type, str):
            if attribute_type.lower() not in all_enum_values:
                raise ValueError(f"Unknown attribute type string: {attribute_type}, available values are: {', '.join(e for e in all_enum_values)}")
            attribute_type_str = attribute_type
        else:
            raise TypeError("attribute_type must be a WellAttributeType or str")
        attribute_type = petrelinterface_pb2.WellAttributeType.Value(attribute_type_str.capitalize())
        template_guid = petrelinterface_pb2.PetrelObjectGuid()
        if template is not None:
            template_guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = template._petrel_object_link._guid,
                sub_type = template._petrel_object_link._sub_type
            )
        request = petrelinterface_pb2.CreateWellAttribute_Request(
            Name = name,
            Type = attribute_type,
            TemplateGuid = template_guid
        )
        ok = self._service_wellattribute.CreateWellAttribute(request)
        if not ok:
            raise PythonToolException("Failed to create well attribute")

    @experimental_method
    def get_well_attributes_as_dataframe(self, 
                                         attribute_filter: List[Union[WellAttributeFilterEnum, str]] = [WellAttributeFilterEnum.All],
                                         wells_filter: Union[WellFolder, SavedSearch] = None) -> pd.DataFrame:
        """Get all well attributes in the current Petrel project as a pandas `DataFrame`, with one row per well and one column per attribute.
        The number of columns in the DataFrame can be filtered by using the `attribute_filter` argument by providing either a list of WellAttributeFilterEnum or strings.
        The number of rows can be filtered by providing either a WellFolder or SavedSearch object in the `wells_filter` argument.

        Args:
            attribute_filter: A list of WellAttributeFilterEnum or strings to filter the attributes to include in the dataframe. Defaults to [WellAttributeFilterEnum.All].
                Available filters are:
                    - 'All': All attributes (Default + User)
                    - 'Default': Only the default attributes
                    - 'User': Only the user defined attributes
            wells_filter (optional): A :class:`WellFolder` or :class:`SavedSearch` object to filter the wells to include in the dataframe. Defaults to None (all wells are included).

        Returns:
            pd.DataFrame: A DataFrame with all well attributes in the current Petrel project.
        
        Raises:
            ValueError: If an unknown attribute filter string is passed.
            ValueError: If the attribute_filter argument is not a list of WellAttributeFilterEnum or strings.
            TypeError: If an individual entry the attribute_filter argument is not a WellAttributeFilterEnum or string.
            TypeError: If the wells_filter argument is not a :class:`WellFolder` or :class:`SavedSearch` object.

        **Example**:

        Get all well attributes in the current Petrel project as a pandas DataFrame.

        .. code-block:: python
            
            from cegalprizm.pythontool import WellAttributeFilterEnum

            petrel.get_well_attributes_as_dataframe(attribute_filter=[WellAttributeFilterEnum.All])
            petrel.get_well_attributes_as_dataframe(attribute_filter=['All'])
            # Mixed filter with WellAttributeFilterEnum and string
            petrel.get_well_attributes_as_dataframe(attribute_filter=[WellAttributeFilterEnum.User, 'Default'])

        **Example**:

        Get all attributes in the current Petrel project for the wells in the specified WellFolder.

        .. code-block:: python

            from cegalprizm.pythontool import WellAttributeFilterEnum
            well_folder = petrel.well_folders["Input/Wells/Other Wells"]
            petrel.get_well_attributes_as_dataframe(attribute_filter=[WellAttributeFilterEnum.All], wells_filter=well_folder)

        """
        self._opened_test()
        attribute_filter_str = []
        if attribute_filter is None or len(attribute_filter) == 0:
            raise ValueError("attribute_filter must be a list of WellAttributeFilterEnum or strings")
        all_enum_values = [e.value for e in WellAttributeFilterEnum]
        for attr in attribute_filter:
            if isinstance(attr, WellAttributeFilterEnum):
                attribute_filter_str.append(attr.value)
            elif isinstance(attr, str):
                if attr not in all_enum_values:
                    raise ValueError(f"Unknown attribute filter string: {attr}")
                attribute_filter_str.append(attr)
            else:
                raise TypeError("attribute_filter must be a list of WellAttributeFilterEnum or str")

        filter_guid = None
        if wells_filter is not None:
            if isinstance(wells_filter, SavedSearch):
                filter_guid = petrelinterface_pb2.PetrelObjectGuid(
                    guid = wells_filter._savedsearch_object_link._guid,
                    sub_type = wells_filter._savedsearch_object_link._sub_type)
            elif isinstance(wells_filter, WellFolder):
                filter_guid = petrelinterface_pb2.PetrelObjectGuid(
                    guid = wells_filter._borehole_collection_object_link._guid,
                    sub_type = wells_filter._borehole_collection_object_link._sub_type)
            else:
                raise TypeError("wells_filter must be a WellFolder or SavedSearch object")
        
        request = petrelinterface_pb2.Borehole_GetAttributes_Request(
            Guid = filter_guid,
            attribute_filter = attribute_filter_str
        )
        responses = self._service_wellattribute.GetProjectWellAttributes(request)
        all_resp = [r for r in responses]
        property_range_handler = PropertyRangeHandler()
        df = property_range_handler.get_dataframe(all_resp)
        if "Name" in df.columns:
            df.insert(0, "Name", df.pop("Name"))
        return df

    @experimental_method
    def set_well_attributes_from_dataframe(self, df: pd.DataFrame, well_name_column:str='Name', create_if_missing:bool=True, ignore_duplicates:bool=False, template_definitions:typing.Dict[str, Template]=None):
        """Set well attributes from a pandas `DataFrame`.  
        The `DataFrame` must contain a column with the well names, which is specified by the `well_name_column` argument.  
        The `DataFrame` must contain the well attributes to be set as columns. The well names in the `DataFrame` must match the well names in the Petrel project.  
        If `create_if_missing` is `True`, any missing well attributes will be created in the Petrel project using the data type specified in the `DataFrame` mapped to well attribute data types.  
        If `ignore_duplicates` is `True`, all wells and attributes with the same name will be updated with the same attribute values, if `False` they will be skipped.
        If the `DataFrame` contains well attributes that cannot be written to, they will be ignored.  
        If creating a new well attribute, and the column is empty, you must specify the data type when creating the `DataFrame`.  
        If you do not specify the data type of a empty column, the column will be created as a continuous well attribute.  
        If the column is not empty, the data type will be inferred from the column values.  

        The pandas data type will be mapped as follows:  
            - `float64` -> Continuous  
            - `Int32` -> Discrete  
            - `object` -> String  
            - `boolean` -> Boolean  

        Date columns must be specified when creating the dataframe using the pandas `parse_dates` argument with the date column names, see example.  
        Using the `template_definitions` argument, you can specify the template to use for each new well attribute in the `DataFrame` by mapping the column name to the template to use.  
        The template must be a :class:`Template` object for 'continuous' well attributes or :class:`DiscreteTemplate` for 'discrete' well attributes.  
        The Ocean API is limited to only allow setting the template when the well attribute is created, meaning it is not possible to change the template for an existing well attribute  

        Args:
            df (pd.DataFrame): The DataFrame containing the well attributes to be set.
            well_name_column (str): The name of the column in the DataFrame containing the well names. Defaults to 'Name'.
            create_if_missing (bool): If True, any missing well attributes will be created in the Petrel project. Defaults to True.
            ignore_duplicates (bool): If False, all wells and attributes with the same Petrel name will be updated with the same attribute values. Defaults to False.
            template_definitions (dict[str, Template]): A dictionary mapping the column names to the templates to use for new discrete or continuous well attribute. If not defined, default templates will be used. Defaults to None.
        
        Raises:
            KeyError: If a well name in the DataFrame does not exist in the Petrel project.
            TypeError: If the well_name_column argument is not a string.
            TypeError: If the df argument is not a pandas DataFrame.
            TypeError: If the ignore_duplicates argument is not a boolean.
            TypeError: If the create_if_missing argument is not a boolean.
            TypeError: If the template_definitions argument is not a dictionary or None.
            PythonToolException: If the well attributes cannot be set for any reason.
        
        **Example**:

        Read a CSV file containing well attributes, both existing and new attributes, and set them in the Petrel project.

        .. code-block:: python

            # Define the column data types in the CSV file when the columns are empty.
            column_definitions = {
                'NewDiscreteColumn': 'Int32',
                'NewBoolColumn': 'boolean',
                'NewContinuousColumn': 'float64',
                'NewStringColumn': 'object'
            }
            # Create a DataFrame from a source, e.g. a CSV file.
            df = pd.read_csv(
                "well_attributes.csv",
                dtype=column_definitions,
                parse_dates=['Spud date','Simulation export date','NewDateColumn']
            )
            # Define the template to use for new discrete or continuous well attribute.
            template_definitions = {
                'NewDiscreteColumn': petrel.discrete_templates["path/to/discrete_template"],
                'NewContinuousColumn': petrel.templates["path/to/continuous_templates"]
            }
            # Set the well attributes in the Petrel project.
            petrel.set_well_attributes_from_dataframe(
                df,
                well_name_column='Name',
                create_if_missing=True,
                ignore_duplicates=False,
                template_definitions=template_definitions
            )
        """
        if not isinstance(well_name_column, str):
            raise TypeError("well_name_column must be a string")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(ignore_duplicates, bool):
            raise TypeError("ignore_duplicates must be a boolean")
        if not isinstance(create_if_missing, bool):
            raise TypeError("create_if_missing must be a boolean")
        if not isinstance(template_definitions, (dict, type(None))):
            raise TypeError("template_definitions must be a dictionary or None")
        if df.index.empty:
            return
        
        self._opened_test()
        project_wells = self.wells
        flatten_wells = utils.deep_flatten_list(project_wells)
        if create_if_missing:
            self._create_well_attribute_if_missing(df, well_name_column, template_definitions)
        for index, row in df.iterrows():
            well_key = row[well_name_column]
            wells = [w for w in flatten_wells if w.petrel_name == well_key]
            if len(wells) == 0:
                raise KeyError(f"Well '{well_key}' not found in the project.")
            try:
                if len(wells) > 1 and ignore_duplicates:
                    warn(f"Warning: Found multiple wells with the same name '{well_key}'. Skipping.")
                    continue
                one_row_df = df.iloc[[index]]
                for well in wells:
                    well.attributes.set_values(one_row_df, ignore_duplicates)
            except Exception as e:
                raise PythonToolException(f"Failed to set well attributes for well '{well_key}': {e}")

    @experimental_method
    def _create_well_attribute_if_missing(self, df, well_name_column, template_definitions: typing.Dict[str, Template]=None):
        """Create well attributes if they are missing in the Petrel project.

        Args:
            df (pd.DataFrame): The DataFrame containing the well attributes to be set.
            well_name_column (str): The name of the column in the DataFrame containing the well names.
            template_definitions (dict[str, Template]): A dictionary mapping the column names to the templates to use for each new well attribute.

        Returns:
            bool: True
        
        Raises:
            TypeError: If the column type is not supported for well attributes.
        """
        iterable_request = (
            petrelinterface_pb2.CreateWellAttribute_Request(
                Name=name,
                Type=self._get_attribute_type(df[name].dtype.name.lower(), name),
                TemplateGuid=self._get_attribute_template(template_definitions.get(name) if template_definitions is not None and name in template_definitions else None),
            )
            for name in df.columns if name != well_name_column
        )
        response = self._service_wellattribute.CreateWellAttributeIfMissing(iterable_request)
        for i in range(len(response.values)):
            warn(f"Well attribute '{response.values[i]}' already exists in the project. This attribute cannot be edited. Please rename the corresponding column in the DataFrame to create a separate well attribute.")

    def _get_attribute_template(self, template):
        template_guid = petrelinterface_pb2.PetrelObjectGuid()
        if template is not None:
            template_guid = petrelinterface_pb2.PetrelObjectGuid(
                guid = template._petrel_object_link._guid,
                sub_type = template._petrel_object_link._sub_type
            )
        return template_guid

    def _get_attribute_type(self, column_type: str, attr_name) -> int:
        if column_type == 'float64':
            return petrelinterface_pb2.WellAttributeType.Value(WellAttributeType.Continuous.value.capitalize())
        elif column_type == 'int32' or column_type == 'int64':
            return petrelinterface_pb2.WellAttributeType.Value(WellAttributeType.Discrete.value.capitalize())
        elif column_type == 'object':
            return petrelinterface_pb2.WellAttributeType.Value(WellAttributeType.String.value.capitalize())
        elif column_type == 'boolean' or column_type == 'bool':
            return petrelinterface_pb2.WellAttributeType.Value(WellAttributeType.Boolean.value.capitalize())
        elif column_type == 'datetime64[ns]':
            return petrelinterface_pb2.WellAttributeType.Value(WellAttributeType.Datetime.value.capitalize())
        else:
            raise TypeError(f"Unsupported value type for well attribute '{attr_name}': {column_type}")

    def _find_global_well_logs(self, discrete = False):
        """A dictionary of GUIDs and paths to all global well logs in the current Petrel project.
        Use method get_global_well_log to select one of them. 
        
        Args:
            discrete (bool, optional): Discrete (True) or continuous (False) global well logs. Defaults to False.
        Returns:
            Dictionary: All global well logs with GUID as key and path as value.
        """
        if discrete:
            request_string = 'find global discrete well logs'
        else:
            request_string = 'find global well logs'
        return self._find_paths_by_guids(request_string)

    def _find_global_observed_data_sets(self):
        """A dictionary of GUIDs and paths to all global observed data sets in the current Petrel project.
        Use method get_global_observed_data_set to select one of them. 
        
        Returns:
            Dictionary: All global observed data sets with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find global observed data sets')
    
    def _find_grid_properties(self, discrete = False):
        """A dictionary of GUIDs and paths to all grid properties in the current Petrel project.
        Use method get_grid_property to select one of them. 

        Args:
            discrete (bool, optional): Discrete (True) or continuous (False) grid properties. Defaults to False.

        Returns:
            Dictionary: All grid properties with GUID as key and path as value.
        """
        if discrete:
            request_string = 'find discrete grid properties'
        else:
            request_string = 'find grid properties'

        return self._find_paths_by_guids(request_string)

    def _find_grids(self):
        """A dictionary of GUIDs and paths to all grids in the current Petrel project.
        Use method get_grid to select one of them. 
        
        Returns:
            Dictionary: All grids with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find grids')

    def _find_horizon_properties(self):
        """A dictionary of GUIDs and paths to all horizon properties in the current Petrel project.
        Use method get_horizon_property to select one of them. 

        Returns:
            Dictionary: All horizon properties with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find horizon properties 3d')

    def _find_horizon_interpretation_3ds(self):
        """A dictionary of GUIDs and paths to all horizon interpretations in the current Petrel project.
        Use method get_horizon_interpretation to select one of them. 

        Returns:
            Dictionary: All horizon interpretations with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find horizon interpretations 3d')

    def _find_horizon_interpretations(self):
        """A dictionary of GUIDs and paths to all horizon interpretations in the current Petrel project.
        Use method get_horizon_interpretation to select one of them. 

        Returns:
            Dictionary: All horizon interpretations with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find horizon interpretations')

    def _find_pointsets(self):
        """A dictionary of GUIDs and paths to all pointsets in the current Petrel project.
        Use method get_pointset to select one of them. 

        Args:
            discrete (bool, optional): Discrete (True) or continuous (False) pointsets. Defaults to False.

        Returns:
            Dictionary: All pointsets with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find pointsets')

    def _find_polylinesets(self):
        """A dictionary of GUIDs and paths to all polylinesets in the current Petrel project.
        Use method get_polylineset to select one of them. 

        Returns:
            Dictionary: All polylinesets with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find polylinesets')
    
    def _find_fault_interpretations(self):
        """A dictionary of GUIDs and paths to all fault interpretations in the current Petrel project.
        Use method get_fault_interpretation to select one of them. 

        Returns:
            Dictionary: All fault interpretations with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find fault interpretations')
    
    def _find_interpretation_folders(self):
        """A dictionary of GUIDs and paths to all interpretation folders (InterpretationCollections) in the current Petrel project.
        Use method get_interpretation_folder to select one of them. 

        Returns:
            Dictionary: All interpretation folders with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find interpretation collections')

    def _find_wavelets(self):
        return self._find_paths_by_guids('find wavelets')

    def _find_workflows(self):
        return self._find_paths_by_guids('find workflows')

    def _find_reference_variables(self):
        return self._find_paths_by_guids('find reference variables')

    def _find_properties(self, discrete = False):
        """ Alias for method find_grid_properties().
        """
        return self._find_grid_properties(discrete = discrete)

    def _find_property_collections(self):
        """A dictionary of GUIDs and paths to all grid property collections in the current Petrel project.
        Use method get_property_collection to select one of them. 

        Returns:
            Dictionary: All grid property collections with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find property collections')

    def _find_surfaces(self):
        """A dictionary of GUIDs and paths to all surfaces in the current Petrel project.
        Use method get_surface to select one of them. 

        Returns:
            Dictionary: All surfaces with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find surfaces')

    def _find_surface_attributes(self, discrete = False):
        """A dictionary of GUIDs and paths to all surface attributes in the current Petrel project.
        Use method get_surface_attribute to select one of them. 
        
        Args:
            discrete (bool, optional): Discrete (True) or continuous (False) surface attributes. Defaults to False.
        
        Returns:
            Dictionary: All surface attributes with GUID as key and path as value.
        """
        if discrete:
            request_string = 'find discrete surface properties'
        else:
            request_string = 'find surface properties'
        return self._find_paths_by_guids(request_string)

    def _find_seismic_2ds(self):
        """ Alias for method find_seismic_lines().
        """
        return self._find_seismic_lines()

    def _find_seismic_cubes(self):
        """A dictionary of GUIDs and paths to all seismic cubes in the current Petrel project.
        Use method get_seismic_cube to select one of them. 

        Returns:
            Dictionary: All seismic cubes with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find seismic cubes')

    def _find_seismic_lines(self):
        """A dictionary of GUIDs and paths to all seismic line objects in the current Petrel project.
        Use method get_seismic_line to select one of them.

        Returns:
            Dictionary: All seismic line objects with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find seismic 2ds')

    def _find_markercollections(self):
        """A dictionary of GUIDs and paths to all marker collections in the current Petrel project.
        Use method get_markercollection to select one of them.

        Returns:
            Dictionary: All marker collections with path as key and name as value.
        """
        return self._find_paths_by_guids('find marker collections')

    def _find_well_attributes(self):
        """A dictionary of GUIDs and paths to all well attributes in the current Petrel project.

        Returns:
            Dictionary: All well attributes with path as key and name as value.
        """
        return self._find_paths_by_guids('find well attributes')

    def _find_well_logs(self, discrete = False):
        """A dictionary of GUIDs and paths to all well logs in the current Petrel project.
        Use method get_well_log to select one of them. 

        Args:
            discrete (bool, optional): Discrete (True) or continuous (False) global well logs. Defaults to False.

        Returns:
            Dictionary: All well logs with GUID as key and path as value.
        """
        if discrete:
            request_string = 'find discrete well logs'
        else:
            request_string = 'find well logs'
         
        return self._find_paths_by_guids(request_string)

    def _find_wells(self):
        """A dictionary of GUIDs and paths to all wells in the current Petrel project.
        Use method get_well to select one of them. 

        Returns:
            Dictionary: All wells with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find boreholes')
    
    def _find_well_folders(self):
        """A dictionary of GUIDs and paths to all well folders in the current Petrel project.
        Use method get_well_folder to select one of them. 

        Returns:
            Dictionary: All well folders with GUID as key and path as value.
        """
        return self._find_paths_by_guids('find borehole collections')
    
    def _find_observed_data(self):
        """A dictionary of observed data"""
        return self._find_paths_by_guids('find observed data')

    def _find_observed_data_sets(self):
        """A dictionary of observed data set"""
        return self._find_paths_by_guids('find observed data set')

    def _find_templates(self):
        """A dictionary of templates"""
        return self._find_paths_by_guids('find templates')
    
    def _find_discrete_templates(self):
        """A dictionary of discrete templates"""
        return self._find_paths_by_guids('find discrete templates')
    
    def _find_checkshots(self):
        """A dictionary of checkshots"""
        return self._find_paths_by_guids('find checkshots')

    def _find_saved_searches(self):
        """A dictionary of saved searches"""
        return self._find_paths_by_guids('find saved searches')

    def _find_paths_by_guids(self, request_string):
        self._opened_test()
        request = petrelinterface_pb2.ProtoString(value = request_string)
        responses = self._service_project.GetStringsMap(request)
        result = {}
        for response in responses:
            Utils.protobuf_map_to_dict(response.string_to_string_map, result)
        return result

    def _find_well_surveys(self):
        """A list of PetrelObjectRef of well surveys"""
        return self._find_objects_by_type([
            'find xyz well surveys', 
            'find xytvd well surveys', 
            'find dxdytvd well surveys', 
            'find mdinclazim well surveys', 
            'find explicit well surveys'
            ])

    def _find_objects_by_type(self, request_strings: list) -> typing.List[PetrelObjectRef]:
        self._opened_test()
        request = Primitives.StringArray(values = request_strings)
        responses = self._service_project.Project_GetPetrelObjectsByType(request)
        return list(responses)

    def _get_markercollection(self, path):
        """Get a marker collection in Petrel as a MarkerCollection by its path or GUID.
        
        Args:
            path (string): Either the path or GUID of the marker collection.

        Returns:
            MarkerCollection: Reference to a marker collection object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_markercollection.GetMarkerCollection(request)
        if(reply.guid):
            petrel_object_link = MarkerCollectionGrpc(reply.guid, self)
            return MarkerCollection(petrel_object_link)
        else:
            return None

    def _get_global_well_log(self, path, discrete = False):
        """Get a global well log in Petrel as a GlobalWellLog or DiscreteGlobalWellLog by its path or GUID as printed by method show_global_well_logs.

        Args:
            path (string): Either the path or GUID of the global well log.
            discrete (bool, optional): Get a discrete (True) or continuous (False) global well log. Defaults to False.

        Returns:
            GlobalWellLog or DiscreteGlobalWellLog: Reference to a global well log object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.GetGlobalWellLog_Request(node_path = path, discrete_logs = discrete)
        reply = self._service_globalwelllog.GetGlobalWellLog(request)
        if not reply.guid:
            return None
        if discrete:
            return DiscreteGlobalWellLog(DiscreteGlobalWellLogGrpc(reply.guid, self))
        return GlobalWellLog(GlobalWellLogGrpc(reply.guid, self))
    
    def _get_global_observed_data_set(self, path):
        """Get a global observed data setin Petrel as a GlobalObservedDataSet by its path or GUID

        Args:
            path (string): Either the path or GUID of the global observed data set.

        Returns:
            GlobalObservedDataSet: Reference to a global observed data set object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_globalobserveddatasets.GetGlobalObservedDataSet(request)
        if reply.guid:
            petrel_object_link = GlobalObservedDataSetsGrpc(reply.guid, self)
            return GlobalObservedDataSet(petrel_object_link)
        else:
            return None
        

    def _get_grid(self, path):
        """Get a grid in Petrel as a Grid object by its path or GUID as printed by method show_grids.

        Args:
            path (string): Either the path or GUID of the grid.

        Returns:
            Grid: Reference to a grid object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_grid.GetGrid(request)
        if reply.guid:
            petrel_object_link = GridGrpc(reply.guid, self)
            return Grid(petrel_object_link)
        else:
            return None

    def _get_grid_property(self, path, discrete = False):
        """Get a grid property in Petrel as a GridProperty object by its path or GUID as printed by method show_grid_properties.

        Args:
            path (string): Either the path or GUID of the grid property.

        Args:
            path (string): Either the path or GUID of the grid.
            discrete (bool, optional): Get a discrete (True) or continuous (False) grid property. Defaults to False.

        Returns:
            GridProperty: Reference to a grid property object in the current Petrel project.
        """
        request = petrelinterface_pb2.Property_Request(node_path = path, discrete = discrete)
        reply = self._service_grid_property.GetGridProperty(request)
            
        if not reply.guid:
            return None
        if discrete:
            return GridDiscreteProperty(GridDiscretePropertyGrpc(reply.guid, self))
    
        return GridProperty(GridPropertyGrpc(reply.guid, self))

    def _get_horizon_property(self, path):
        """Get a horizon property in Petrel as a HorizonProperty3d object by its path or GUID as printed by method show_horizon_properties.

        Args:
            path (string): Either the path or GUID of the horizon property object.

        Returns:
            HorizonPropery3d: Reference to a horizon property object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_horizon.GetHorizonProperty3d(request)
        if reply.guid:
            petrel_object_link = HorizonProperty3dGrpc(reply.guid, self)
            return HorizonProperty3d(petrel_object_link)
        else:
            return None

    def _get_horizon_interpretation_3d(self, path):
        """Get a horizon interpretation in Petrel as a HorizonInterpretation3d object by its path or GUID as printed by method show_horizon_interpretation.

        Args:
            path (string): Either the path or GUID of the horizon interpretation.

        Returns:
            HorizonInterpretation3d: Reference to a horizon interpretation object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_horizon.GetHorizonInterpretation3d(request)
        if reply.guid:
            petrel_object_link = HorizonInterpretation3dGrpc(reply.guid, self)
            return HorizonInterpretation3d(petrel_object_link)
        else:
            return None

    def _get_horizon_interpretation(self, path):
        """Get a horizon interpretation in Petrel as a HorizonInterpretation3d object by its path or GUID as printed by method show_horizon_interpretation.

        Args:
            path (string): Either the path or GUID of the horizon interpretation.

        Returns:
            HorizonInterpretation3d: Reference to a horizon interpretation object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_horizon_interpretation.GetHorizonInterpretation(request)
        if reply.guid:
            petrel_object_link = HorizonInterpretationGrpc(reply.guid, self)
            return HorizonInterpretation(petrel_object_link)
        else:
            return None
        
    def _get_fault_interpretation(self, path):
        """Get a fault interpretation in Petrel as a FaultInterpretation object by its path or GUID.
        
        Args:
            path (string): Either the path or GUID of the fault interpretation.
        
        Returns:
            FaultInterpretation: Reference to a fault interpretation object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_faultinterpretation.GetFaultInterpretation(request)
        if reply.guid:
            petrel_object_link = FaultInterpretationGrpc(reply.guid, self)
            return FaultInterpretation(petrel_object_link)
        else:
            return None

    def _get_wavelet(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_wavelet.GetWavelet(request)
        if reply.guid:
            petrel_object_link = WaveletGrpc(reply.guid, self)
            return Wavelet(petrel_object_link)
        else:
            return None

    def _get_workflow(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_workflow.GetWorkflow(request)
        if reply.guid:
            petrel_object_link = WorkflowGrpc(reply.guid, self)
            return Workflow(petrel_object_link)
        else:
            return None

    def _get_reference_variable(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_referencevariable.GetReferenceVariable(request)
        if reply.guid:
            petrel_object_link = ReferenceVariableGrpc(reply.guid, self)
            return ReferenceVariable(petrel_object_link)
        else:
            return None

    def _get_pointset(self, path):
        """Get a point set in Petrel as a PointSet object by its path or GUID as printed by method show_pointsets.

        Args:
            path (string): Either the path or GUID of the pointset.

        Returns:
            PointSet: Reference to a pointset object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_points.GetPointSet(request)
        if reply.guid:
            petrel_object_link = PointSetGrpc(reply.guid, self)
            return PointSet(petrel_object_link)
        else:
            return None

    def _get_polylineset(self, path):
        """Get a polyline set in Petrel as a PolylineSet by its path or GUID as printed by method show_polylinesets.

        Args:
            path (string): Either the path or GUID of the polylineset.

        Returns:
            PolylineSet: Reference to a polylineset object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_polylines.GetPolylineSet(request)
        if reply.guid:
            petrel_object_link = PolylineSetGrpc(reply.guid, self)
            return PolylineSet(petrel_object_link)
        else:
            return None

    def _get_property(self, path, discrete = False):
        """Alias for method _get_grid_property().
        """
        return self._get_grid_property(path, discrete = discrete)

    def _get_property_collection(self, path):
        """Get a property collection in Petrel as a PropertyCollection object by its path or GUID as printed by method show_property_collections.

        Args:
            path (string): Either the path or GUID of the grid property collection.

        Returns:
            PropertyCollection: Reference to a property collection object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.Property_Request(node_path = path)
        reply = self._service_grid_property.GetPropertyCollection(request)
        if reply.guid:
            petrel_object_link = PropertyCollectionGrpc(reply.guid, self)
            return PropertyCollection(petrel_object_link)
            
        else:
            return None

    def _get_seismic_2d(self, path):
        """Get a seismic line object in Petrel as a SeismicLine object by its path or GUID as printed by method show_seismic2ds.

        This is an alias for method _get_seismic_line.

        Args:
            path (string): Either the path or GUID of the seismic line object.

        Returns:
            SeismicLine: Reference to a seismic line object in the current Petrel project.
        """
        return self._get_seismic_line(path)

    def _get_seismic_cube(self, path):
        """Get a seismic cube in Petrel as a SeismicCube object by its path or GUID as printed by method show_seismic_cubes.

        Args:
            path (string): Either the path or GUID of the seismic cube.

        Returns:
            SeismicCube: Reference to a seismic cube object in the current Petrel project.
        """
        self._opened_test()

        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)        
        reply = self._service_seismic.GetSeismicCube(request)
        
        if reply.guid:
            petrel_object_link = SeismicCubeGrpc(reply.guid, self)
            return SeismicCube(petrel_object_link)
        else:
            return None

    def _get_seismic_line(self, path):
        """Get a seismic line object in Petrel as a SeismicLine object by its path or GUID as printed by method show_seismic2ds.

        Args:
            path (string): Either the path or GUID of the seismic line object.

        Returns:
            SeismicLine: Reference to a seismic line object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_seismic_2d.GetSeismic2D(request)
        if reply.guid:
            petrel_object_link = Seismic2DGrpc(reply.guid, self)
            return SeismicLine(petrel_object_link)
        else:
            return None

    def _get_surface(self, path):
        """Get a surface in Petrel as a Surface object by its path or GUID as printed by method show_surfaces.

        Args:
            path (string): Either the path or GUID of the surface.

        Returns:
            Surface: Reference to a surface object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_surface.GetSurface(request)
        if reply.guid:
            petrel_object_link = SurfaceGrpc(reply.guid, self)
            return Surface(petrel_object_link)
        return None
        
    def _get_surface_attribute(self, path, discrete = False):
        """Get a surface attribute in Petrel as a SurfaceAttribute or SurfaceDiscreteAttribute by its path or GUID as printed by method show_surface_attributes.

        Args:
            path (string): Either the path or GUID of the surface attribute.
            discrete (bool, optional): Get a discrete (True) or continuous (False) surface attribute. Defaults to False.

        Returns:
            SurfaceAttribute or SurfaceDiscreteAttribute: Reference to a surface attribute object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.Property_Request(node_path = path, discrete = discrete)
        reply = self._service_surface_property.GetSurfaceProperty(request)
        if not reply.guid:
            return None
        if discrete:
            return SurfaceDiscreteAttribute(SurfaceDiscretePropertyGrpc(reply.guid, self))
        
        return SurfaceAttribute(SurfacePropertyGrpc(reply.guid, self))
    
    def _get_well(self, path):
        """Get a well in Petrel as a Well by its path or GUID as printed by method show_wells.

        Args:
            path (string): Either the path or GUID of the well.

        Returns:
            Well: Reference to a well object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_borehole.GetBorehole(request)
        if reply.guid:
            petrel_object_link = BoreholeGrpc(reply.guid, self)
            return Well(petrel_object_link)
        else:
            return None
        
    def _get_well_folder(self, path):
        """Get a well folder in Petrel as a WellFolder by its path or GUID as printed by method show_well_folders.

        Args:
            path (string): Either the path or GUID of the well folder.

        Returns:
            WellFolder: Reference to a well folder object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_boreholecollection.GetBoreholeCollectionGrpc(request)
        if reply.guid:
            petrel_object_link = BoreholeCollectionGrpc(reply.guid, self)
            return WellFolder(petrel_object_link)
        else:
            return None


    def _get_well_log(self, path, discrete = False):
        """Get a well log in Petrel as a WellLog or DiscreteWellLog by its path or GUID as printed by method show_well_logs.

        Args:
            path (string): Either the path or GUID of the well log.
            discrete (bool, optional): Get a discrete (True) or continuous (False) well log. Defaults to False.

        Returns:
            WellLog or DiscreteWellLog: Reference to a well log object in the current Petrel project.
        """
        self._opened_test()
        request = petrelinterface_pb2.GetWellLog_Request(node_path = path, discrete_logs = discrete)
        reply = self._service_welllog.GetWellLog(request)
        if not reply.guid:
            return None
        if discrete:
            return DiscreteWellLog(DiscreteWellLogGrpc(reply.guid, self))
        return WellLog(WellLogGrpc(reply.guid, self))

    def _get_xyz_well_survey(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_xyz_well_survey.GetXyzWellSurvey(request)
        if reply.guid:
            petrel_object_link = XyzWellSurveyGrpc(reply.guid, self)
            return WellSurvey(petrel_object_link)
        else:
            return None

    def _get_xytvd_well_survey(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_xytvd_well_survey.GetXytvdWellSurvey(request)
        if reply.guid:
            petrel_object_link = XytvdWellSurveyGrpc(reply.guid, self)
            return WellSurvey(petrel_object_link)
        else:
            return None

    def _get_dxdytvd_well_survey(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_dxdytvd_well_survey.GetDxdytvdWellSurvey(request)
        if reply.guid:
            petrel_object_link = DxdytvdWellSurveyGrpc(reply.guid, self)
            return WellSurvey(petrel_object_link)
        else:
            return None

    def _get_mdinclazim_well_survey(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_mdinclazim_well_survey.GetMdinclazimWellSurvey(request)
        if reply.guid:
            petrel_object_link = MdinclazimWellSurveyGrpc(reply.guid, self)
            return WellSurvey(petrel_object_link)
        else:
            return None

    def _get_explicit_well_survey(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_explicit_well_survey.GetExplicitWellSurvey(request)
        if reply.guid:
            petrel_object_link = ExplicitWellSurveyGrpc(reply.guid, self)
            return WellSurvey(petrel_object_link)
        else:
            return None

    def _get_observed_data(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_observeddata.GetObservedData(request)
        if reply.guid:
            petrel_object_link = ObservedDataGrpc(reply.guid, self)
            return ObservedData(petrel_object_link)
        else:
            return None

    def _get_observed_data_set(self, path):
        self._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(node_path = path)
        reply = self._service_observeddataset.GetObservedDataSet(request)
        if reply.guid:
            petrel_object_link = ObservedDataSetGrpc(reply.guid, self)
            return ObservedDataSet(petrel_object_link)
        else:
            return None

    def _get(self, obj_type, path):
        if obj_type == 'grid':
            return self._get_grid(path)

        if obj_type == 'grid property':
            return self._get_grid_property(path, discrete = False)

        if obj_type == 'grid discrete property':
            return self._get_grid_property(path, discrete = True)

        if obj_type == 'seismic cube':
            return self._get_seismic_cube(path)

        if obj_type == 'seismic 2d':
            return self._get_seismic_2d(path)

        if obj_type == 'surface':
            return self._get_surface(path)

        if obj_type == 'surface property':
            return self._get_surface_attribute(path)

        if obj_type == 'marker collection':
            return self._get_markercollection(path)

        if obj_type == 'horizon interpretation 3d':
            return self._get_horizon_interpretation_3d(path)

        if obj_type == 'horizon interpretation':
            return self._get_horizon_interpretation(path)

        if obj_type == 'horizon property 3d':
            return self._get_horizon_property(path)

        if obj_type == 'surface discrete property':
            return self._get_surface_attribute(path, discrete = True)

        if obj_type == 'well':
            return self._get_well(path)

        if obj_type == 'well log':
            return self._get_well_log(path, discrete = False)

        if obj_type == 'discrete well log':
            return self._get_well_log(path, discrete = True)

        if obj_type == 'global well log':
            return self._get_global_well_log(path, discrete = False)

        if obj_type == 'global discrete well log':
            return self._get_global_well_log(path, discrete = True)

        if obj_type == 'global observed data set':
            return self._get_global_observed_data_set(path)

        if obj_type == 'pointset':
            return self._get_pointset(path)

        if obj_type == 'polylineset':
            return self._get_polylineset(path)

        if obj_type == 'wavelet':
            return self._get_wavelet(path)

        if obj_type == 'workflow':
            return self._get_workflow(path)

        if obj_type == 'referencevariable':
            return self._get_reference_variable(path)
        
        if obj_type == 'xyz well survey':
            return self._get_xyz_well_survey(path)

        if obj_type == 'xytvd well survey':
            return self._get_xytvd_well_survey(path)

        if obj_type == 'dxdytvd well survey':
            return self._get_dxdytvd_well_survey(path)

        if obj_type == 'mdinclazim well survey':
            return self._get_mdinclazim_well_survey(path)

        if obj_type == 'explicit well survey':
            return self._get_explicit_well_survey(path)

        if obj_type == "observed data":
            return self._get_observed_data(path)
        
        if obj_type == "observed data set":
            return self._get_observed_data_set(path)
        
        if obj_type == "fault interpretation":
            return self._get_fault_interpretation(path)

        return None
        
    def _opened_test(self):
        if self._opened == PetrelConnectionState.UNOPENED:
            raise Exception('The connection is not opened. Call the open() method')
        if self._opened == PetrelConnectionState.CLOSED:
            raise Exception('The connection is closed. Make a new PetrelConnection instance')

    @property
    def discrete_global_well_logs(self) -> PO_DiscreteGlobalWellLogs:
        """Retrieve all discrete well logs in Petrel as DiscreteGlobalWellLog objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).  

        If multiple objects have the same path, a list of them is returned.

        Returns:
            DiscreteGlobalWellLogs: A dictionary of DiscreteGlobalWellLog objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.discrete_global_well_logs['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_DiscreteGlobalWellLogs(self)

    @property
    def discrete_grid_properties(self) -> PO_DiscreteProperties:
        """Retrieve all discrete grid properties in Petrel as GridDiscreteProperty objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            DiscreteProperties: A dictionary of GridDiscreteProperty objects by their path.
        
        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.discrete_grid_properties['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_DiscreteProperties(self)
    
    @property
    def discrete_properties(self) -> PO_DiscreteProperties:
        """DeprecationWarning: 'discrete_properties' has been removed. Use 'discrete_grid_properties' instead
        """
        warn("'discrete_properties' has been removed. Use 'discrete_grid_properties' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'discrete_properties' has been removed. Use 'discrete_grid_properties' instead")     

    @property
    def discrete_well_logs(self) -> PO_DiscreteWellLogs:
        """Retrieve all discrete well logs in Petrel as DiscreteWellLog objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            DiscreteWellLogs: A dictionary of DiscreteWellLog objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.discrete_well_logs['Petrel path']

        With 'petrel' as your defined PetrelConnection. 
        """
        return PO_DiscreteWellLogs(self)

    @property
    def global_well_logs(self) -> PO_GlobalWellLogs:
        """Retrieve all global well logs in Petrel as GlobalWellLog objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            GlobalWellLogs: A dictionary of GlobalWellLog objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.global_well_logs['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_GlobalWellLogs(self)

    @property
    def global_observed_data_sets(self) -> PO_GlobalObservedDataSets:
        """Retrieve all global observed data sets  in Petrel as GlobalObservedDataSet objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            GlobalObservedDataSets: A dictionary of GlobalObservedDataSet objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.global_observed_data_sets['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_GlobalObservedDataSets(self)

    @property
    def grid_properties(self) -> PO_Properties:
        """Retrieve all grid properties in Petrel as GridProperty objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Properties: A dictionary of GridProperty objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.grid_properties['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Properties(self)

    @property
    def grids(self) -> PO_Grids:
        """Retrieve all grids in Petrel as Grid objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Grids: A dictionary of Grid objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.grids['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Grids(self)

    @property
    def horizon_interpretation_3ds(self) -> PO_HorizonInterpretation3Ds:
        """Retrieve all 3D horizon interpretation objects in Petrel as HorizonInterpretation3d objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            HorizonInterpretation3Ds: A dictionary of HorizonInterpretation3d objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.horizon_interpretation_3ds['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_HorizonInterpretation3Ds(self)

    @property
    def horizon_interpretations(self) -> PO_HorizonInterpretations:
        """Retrieve all seismic horizon in Petrel as HorizonInterpretation objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            HorizonInterpretation: A dictionary of HorizonInterpretation objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.horizon_interpretations['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """          
        return PO_HorizonInterpretations(self)

    @property
    def horizon_properties(self) -> PO_HorizonProperties:
        """Retrieve all horizon properties in Petrel as HorizonProperty objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            HorizonProperties: A dictionary of HorizonProperty objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.horizon_properties['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """        
        return PO_HorizonProperties(self)

    @property
    def pointsets(self) -> PO_PointSets:
        """Retrieve all point sets in Petrel as PointSet objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            PointSets: A dictionary of PointSet objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.pointsets['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_PointSets(self)

    @property
    def polylinesets(self) -> PO_PolylineSets:
        """Retrieve all polyline sets in Petrel as PolylineSet objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            PolylineSets: A dictionary of PolylineSet objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.polylinesets['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_PolylineSets(self)

    @property
    def wavelets(self) -> PO_Wavelets:
        """Retrieve all wavelets in Petrel as Wavelet objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Wavelets: A dictionary of Wavelet objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.wavelets['Petrel path']

        With 'petrel' as your defined PetrelConnection. 
        """
        return PO_Wavelets(self)

    @property # type: ignore
    def workflows(self) -> PO_Workflows:
        """Retrieve all workflows in Petrel as Workflows objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Workflows: A dictionary of Workflow objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.workflows['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """         
        return PO_Workflows(self)

    @property
    def well_surveys(self) -> PO_WellSurveys:
        """Retrieve all well surveys in Petrel as WellSurvey objects and collect them in a dictionary with their paths as keys.
        All 5 types of well surveys in Petrel are treated as one object in Python Tool Pro
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            Properties: A dictionary of WellSurveys objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.well_surveys['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_WellSurveys(self)

    @property
    def properties(self) -> PO_Properties:
        """DeprecationWarning: 'properties' has been removed. Use 'grid_properties' instead
        """
        warn("'properties' has been removed. Use 'grid_properties' instead", 
             DeprecationWarning, stacklevel=2)
        raise RuntimeError("'properties' has been removed. Use 'grid_properties' instead")

    @property
    def property_collections(self) -> PO_PropertyCollections:
        """Retrieve all property collections in Petrel as PropertyCollection objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            PropertyCollections: A dictionary of PropertyCollection objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.property_collections['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_PropertyCollections(self)

    @property
    def seismic_2ds(self) -> PO_Seismic2Ds:
        """Retrieve all seismic lines in Petrel as SeismicLine objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Seismic2Ds: A dictionary of SeismicLine objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.seismic_2ds['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Seismic2Ds(self)

    @property
    def seismic_cubes(self) -> PO_SeismicCubes:
        """Retrieve all seismic cubes in Petrel as SeismicCube objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Seismic cubes of format SEG-Y are read-only.

        Returns:
            SeismicCubes: A dictionary of SeismicCubes objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.seismic_cubes['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_SeismicCubes(self)

    @property
    def seismic_lines(self) -> PO_Seismic2Ds:
        """Retrieve all seismic lines in Petrel as SeismicLine objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        This is an alias for the member named seismic_2ds of this class.

        Returns:
            Seismic2Ds: A dictionary of SeismicLine objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.seismic_lines['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Seismic2Ds(self)

    @property
    def surface_attributes(self) -> PO_SurfaceAttributes:
        """Retrieve all surface attributes in Petrel as SurfaceAttribute objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            SurfacesAttributes: A dictionary of SurfaceAttribute objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.surface_attributes['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_SurfaceAttributes(self)

    @property
    def surface_discrete_attributes(self) -> PO_SurfaceDiscreteAttributes:
        """Retrieve all discrete surface attributes in Petrel as SurfaceDiscreteAttribute objects and collect them in a dictionary with their paths as keys.

        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            SurfaceDiscreteAttributes: A dictionary of SurfaceDiscreteAttribute objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.surface_discrete_attributes['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_SurfaceDiscreteAttributes(self)
    
    # To maintain naming patterns, create this synonym
    discrete_surface_attributes = surface_discrete_attributes
    
    @property
    def surfaces(self) -> PO_Surfaces:
        """Retrieve all surfaces in Petrel as Surface objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            Surfaces: A dictionary of Surface objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.surfaces['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Surfaces(self)

    @property
    def well_logs(self) -> PO_WellLogs:
        """Retrieve all well logs in Petrel as WellLog objects and collect them in a dictionary with their paths as keys.

        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            WellLogs: A dictionary of WellLog objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.well_logs['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_WellLogs(self)

    @property
    def wells(self) -> PO_Wells:
        """Retrieve all wells in Petrel as Well objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Wells: A dictionary of Well objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.wells['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Wells(self)
    
    @property
    def well_folders(self) -> PO_WellFolders:
        """Retrieve all well folders (BoreholeCollections) in Petrel as WellFolder objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            WellFolders: A dictionary of WellFolder objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.well_folders['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_WellFolders(self)

    @property
    def predefined_global_observed_data(self) -> typing.Dict[str, str]:
        """Returns a dictionary with the predefined global observed data in the petrel project

        keys: the name of the predefined global observed data
        values: the ID used to identify the predefined global observed data
        """
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        response = self._service_project.Project_GetRegisteredObservedDataVersions(request)
        return Utils.protobuf_map_to_dict(response.string_to_string_map)

    @property
    def observed_data_sets(self) -> PO_ObservedDataSets:
        """Retrieve all observed data sets in Petrel as ObservedDataSet objects and collect them in a dictionary with their paths as keys.

        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            ObservedDataSets: A dictionary of ObservedDataSet objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.observed_data_sets['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_ObservedDataSets(self)

    @property
    def markercollections(self) -> PO_MarkerCollections:
        """Retrieve all marker collections in Petrel as MarkerCollection objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            MarkerCollections: A dictionary of MarkerCollection objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.markercollections['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_MarkerCollections(self)
    
    @property
    def faultinterpretations(self) -> PO_FaultInterpretations:
        """Retrieve all fault interpretations in Petrel as FaultInterpretation objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            FaultInterpretations: A dictionary of FaultInterpretation objects by their path.
            
        Examples
        --------
        To retrieve a specific FaultInterpretation use:
        
        my_fault_interpretation = petrel.faultinterpretations['Petrel path']
        
        With 'petrel' as your defined PetrelConnection.
        """
        return PO_FaultInterpretations(self)
    
    @property
    def interpretation_folders(self) -> PO_InterpretationFolders:
        """Retrieve all interpretation folders (InterpretationCollections) in Petrel as InterpretationFolder objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.
        
        Returns:
            InterpretationFolders: A dictionary of InterpretationFolder objects by their path.
            
        Examples
        --------
        To retrieve a specific InterpretationFolder use:
        
        my_interpretation_folder = petrel.interpretation_folders['Petrel path']
        
        With 'petrel' as your defined PetrelConnection.
        """
        return PO_InterpretationFolders(self)

    @property
    def templates(self) -> PO_Templates:
        """Retrieve all templates in Petrel as Template objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            Templates: A dictionary of Template objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.templates['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_Templates(self)
    
    @property
    def discrete_templates(self) -> PO_DiscreteTemplates:
        """Retrieve all discrete templates in Petrel as DiscreteTemplate objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            DiscreteTemplates: A dictionary of DiscreteTemplate objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.discrete_templates['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_DiscreteTemplates(self)
    
    @property
    def checkshots(self) -> PO_CheckShots:
        """Retrieve all check shot versions in Petrel as CheckShot objects and collect them in a dictionary with their paths as keys.
        
        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).
        
        If multiple objects have the same path, a list of them is returned.

        Returns:
            CheckShots: A dictionary of CheckShot objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:
         
        my_var=petrel.checkshots['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_CheckShots(self)

    @property
    def saved_searches(self) -> PO_SavedSearches:
        """Retrieve all saved searches in Petrel as SavedSearch objects and collect them in a dictionary with their paths as keys.

        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.

        Note that saved seaches are read-only and cannot be modified through the Python Tool Pro API.

        Returns:
            SavedSearches: A dictionary of SavedSearch objects by their path.

        Examples
        --------
        To retrieve a specific Petrel object use:

        my_var=petrel.saved_searches['Petrel path']

        With 'petrel' as your defined PetrelConnection.
        """
        return PO_SavedSearches(self)

    @experimental_property
    def well_attributes(self) -> PO_WellAttributes:
        """Retrieve all well attributes in Petrel as WellAttribute objects and collect them in a dictionary with their paths as keys.

        When iterated over, the objects are returned, not their paths (unlike a standard Python dictionary which returns the keys).

        If multiple objects have the same path, a list of them is returned.

        Returns:
            WellAttributes: A dictionary of WellAttribute objects by their path.
        
        Examples
        --------
        To retrieve a specific Petrel object use:

        my_var=petrel.well_attributes['Petrel path']
        
        With 'petrel' as your defined PetrelConnection.
        """
        return PO_WellAttributes(self)

    def available_well_symbols(self) -> typing.List["WellSymbolDescription"]:
        """Returns a list of available well symbol descriptions.

        Returns:
            list[WellSymbolDescription]: a list of available well symbol descriptions for wells

        **Example**:

        Retrieve the complete list of available well symbol descriptions:

        .. code-block:: python

            symbols = petrel.available_well_symbols()

        **Example**:

        Retrieve a specific well symbol description by id:

        .. code-block:: python

            well_symbol = [desc for desc in petrel.available_well_symbols() if desc.id == 23][0]

        **Example**:

        Retrieve a specific well symbol description by the text shown in the Petrel drop-down:

        .. code-block:: python

            well_symbol = [desc for desc in petrel.available_well_symbols() if desc.description == "Condensate, plugged and abandoned"][0]
        """
        self._opened_test()
        request = petrelinterface_pb2.EmptyRequest()
        responses = self._service_project.Project_GetAvailableWellSymbolDescriptions(request)
        descriptions = []
        for response in responses:
            for desc in response.WellSymbolDescriptions:
                descriptions.append((desc.Id, desc.Name, desc.Description))
        descriptions_list = [WellSymbolDescription(index, name, description) for index, name, description in descriptions]
        return descriptions_list

    def create_markercollection(self, name: str) -> MarkerCollection:
        """Creates a new root level MarkerCollection with the given name in the Petrel project.

        Args:
            name (str): The name of the new MarkerCollection.

        Returns
            MarkerCollection: The newly created :class:`MarkerCollection` object.

        Raises:
            TypeError: If the name is not a string.
            ValueError: If the name is empty.

        **Example**:

        Create a new MarkerCollection in the Petrel project:

        .. code-block:: python

            petrel = PetrelConnection()
            marker_collection = petrel.create_markercollection("MyTopLevelMarkerCollection")

        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not name:
            raise ValueError("Name cannot be empty")
        self._opened_test()
        request = petrelinterface_pb2.ProtoString(value = name)
        response = self._service_project.Project_CreateMarkerCollection(request)
        if response.guid:
            grpc_object = MarkerCollectionGrpc(response.guid, self)
            return MarkerCollection(grpc_object)

    def _get_global_well_log_by_guid(self, guid: str, discrete: bool = False) -> typing.Union[DiscreteGlobalWellLog, GlobalWellLog]:
        if discrete:
            return DiscreteGlobalWellLog(DiscreteGlobalWellLogGrpc(guid, self))
        return GlobalWellLog(GlobalWellLogGrpc(guid, self))
    
    def _get_grid_by_guid(self, guid: str) -> Grid:
        petrel_object_link = GridGrpc(guid, self)
        return Grid(petrel_object_link)

    def _get_grid_property_by_guid(self, guid: str, discrete: bool = False) -> typing.Union[GridDiscreteProperty, GridProperty]:
        if discrete:
            return GridDiscreteProperty(GridDiscretePropertyGrpc(guid, self))
        return GridProperty(GridPropertyGrpc(guid, self))

    def _get_markercollection_by_guid(self, guid: str) -> MarkerCollection:
        petrel_object_link = MarkerCollectionGrpc(guid, self)
        return MarkerCollection(petrel_object_link)
    
    def _get_well_attribute_by_guid(self, guid: str) -> WellAttribute:
        petrel_object_link = WellAttributeGrpc(guid, self)
        return WellAttribute(petrel_object_link)

    def _get_fault_interpretation_by_guid(self, guid: str) -> FaultInterpretation:
        petrel_object_link = FaultInterpretationGrpc(guid, self)
        return FaultInterpretation(petrel_object_link)
    
    def _get_interpretation_folder_by_guid(self, guid: str) -> InterpretationFolder:
        petrel_object_link = InterpretationCollectionGrpc(guid, self)
        return InterpretationFolder(petrel_object_link)

    def _get_horizon_property_by_guid(self, guid: str) -> HorizonProperty3d:
        petrel_object_link = HorizonProperty3dGrpc(guid, self)
        return HorizonProperty3d(petrel_object_link)

    def _get_horizon_interpretation_3d_by_guid(self, guid: str) -> HorizonInterpretation3d:
        petrel_object_link = HorizonInterpretation3dGrpc(guid, self)
        return HorizonInterpretation3d(petrel_object_link)

    def _get_horizon_interpretation_by_guid(self, guid: str) -> HorizonInterpretation:
        petrel_object_link = HorizonInterpretationGrpc(guid, self)
        return HorizonInterpretation(petrel_object_link)

    def _get_wavelet_by_guid(self, guid: str) -> Wavelet:
        petrel_object_link = WaveletGrpc(guid, self)
        return Wavelet(petrel_object_link)

    def _get_workflow_by_guid(self, guid: str) -> Workflow:
        petrel_object_link = WorkflowGrpc(guid, self)
        return Workflow(petrel_object_link)

    def _get_reference_variable_by_guid(self, guid: str) -> ReferenceVariable:
        petrel_object_link = ReferenceVariableGrpc(guid, self)
        return ReferenceVariable(petrel_object_link)

    def _get_pointset_by_guid(self, guid: str) -> PointSet:
        petrel_object_link = PointSetGrpc(guid, self)
        return PointSet(petrel_object_link)

    def _get_polylineset_by_guid(self, guid: str) -> PolylineSet:
        petrel_object_link = PolylineSetGrpc(guid, self)
        return PolylineSet(petrel_object_link)

    def _get_property_by_guid(self, guid: str, discrete: bool = False):
        return self._get_grid_property_by_guid(guid, discrete = discrete)    

    def _get_property_collection_by_guid(self, guid: str) -> PropertyCollection:
        petrel_object_link = PropertyCollectionGrpc(guid, self)
        return PropertyCollection(petrel_object_link)

    def _get_seismic_2d_by_guid(self, guid: str):
        return self._get_seismic_line_by_guid(guid)

    def _get_seismic_cube_by_guid(self, guid: str) -> SeismicCube:
        petrel_object_link = SeismicCubeGrpc(guid, self)
        return SeismicCube(petrel_object_link)

    def _get_seismic_line_by_guid(self, guid: str) -> SeismicLine:
        petrel_object_link = Seismic2DGrpc(guid, self)
        return SeismicLine(petrel_object_link)

    def _get_surface_by_guid(self, guid: str) -> Surface:
        petrel_object_link = SurfaceGrpc(guid, self)
        return Surface(petrel_object_link)
        
    def _get_surface_attribute_by_guid(self, guid: str, discrete: bool = False) -> typing.Union[SurfaceDiscreteAttribute, SurfaceAttribute]:
        if discrete:
            return SurfaceDiscreteAttribute(SurfaceDiscretePropertyGrpc(guid, self))
        return SurfaceAttribute(SurfacePropertyGrpc(guid, self))
    
    def _get_well_by_guid(self, guid: str) -> Well:
        petrel_object_link = BoreholeGrpc(guid, self)
        return Well(petrel_object_link)
    
    def _get_well_folder_by_guid(self, guid: str) -> WellFolder:
        petrel_object_link = BoreholeCollectionGrpc(guid, self)
        return WellFolder(petrel_object_link)

    def _get_well_log_by_guid(self, guid: str, discrete: bool = False) -> typing.Union[DiscreteWellLog, WellLog]:
        if discrete:
            return DiscreteWellLog(DiscreteWellLogGrpc(guid, self))
        return WellLog(WellLogGrpc(guid, self))

    def _get_observed_data_by_guid(self, guid: str) -> ObservedData:
        petrel_object_link = ObservedDataGrpc(guid, self)
        return ObservedData(petrel_object_link)

    def _get_observed_data_set_by_guid(self, guid: str) -> ObservedDataSet:
        petrel_object_link = ObservedDataSetGrpc(guid, self)
        return ObservedDataSet(petrel_object_link)

    def _get_global_observed_data_set_by_guid(self, guid: str) -> GlobalObservedDataSet:
        petrel_object_link = GlobalObservedDataSetsGrpc(guid, self)
        return GlobalObservedDataSet(petrel_object_link)

    def _get_template_by_guid(self, guid: str) -> Template:
        petrel_object_link = TemplateGrpc(guid, self)
        return Template(petrel_object_link)

    def _get_discrete_template_by_guid(self, guid: str) -> DiscreteTemplate:
        petrel_object_link = DiscreteTemplateGrpc(guid, self)
        return DiscreteTemplate(petrel_object_link)
    
    def _get_checkshot_by_guid(self, guid: str) -> CheckShot:
        petrel_object_link = CheckShotGrpc(guid, self)
        return CheckShot(petrel_object_link)

    def _get_saved_search_by_guid(self, guid: str) -> SavedSearch:
        petrel_object_link = SavedSearchGrpc(guid, self)
        return SavedSearch(petrel_object_link)
    
    def _pb_PetrelObjectGuid_to_pyobj_wrapper(self, grpc_obj):
        return _pb_grpcobj_to_pyobj(grpc_obj)

    @experimental_method
    def _clearcache(self, cache_name: str = "") -> bool:
        """Private method to clear cache. Can only be used when having a dev .whl. Used for testing. Method may be deleted in future."""
        package_version = _get_version()
        if "dev" in package_version:
            request = petrelinterface_pb2.ProtoString()
            request.value = cache_name
            var = self._service_project.Project_ClearCache(request)
            return var.value
        return False