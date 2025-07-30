# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool.grpc import borehole_grpc, observeddata_grpc, petrelinterface_pb2
from datetime import datetime
import pandas as pd

import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.observeddata_hub import ObservedDataHub, ObservedDataSetHub

class ObservedDataGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(ObservedDataGrpc, self).__init__('observed data', guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("ObservedDataHub", petrel_connection._service_observeddata)

    def __str__(self):
        return 'ObservedData(petrel_name="{}")'.format(self.petrel_name)

    def SetValues(self, values):
        self._plink._opened_test()
        iterable_requests = list((petrelinterface_pb2.ObservedData_SetValues_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
            , values = [v for v in values]
            ) for _ in range(1)
        ))
        ok = self._channel.ObservedData_SetValues((v for v in iterable_requests))
        return ok.value
    
    def GetValues(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.ObservedData_GetValues(request)
        return [item for sublist in responses for item in sublist.values]

    def GetDisplayUnitSymbol(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        return self._channel.ObservedData_DisplayUnitSymbol(request).value

    def GetParentObservedDataSet(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.ObservedData_GetParentObservedDataSet(request)
        return ObservedDataSetGrpc(response.guid, self._plink)
    
class ObservedDataSetGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(ObservedDataSetGrpc, self).__init__('observed data set', guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = typing.cast("ObservedDataSetHub", petrel_connection._service_observeddataset)

    def __str__(self):
        return 'ObservedDataSet(petrel_name="{}")'.format(self.GetPetrelName())

    def GetObservedDataObjects(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.ObservedDataSet_GetObservedDataObjects(request)
        guids = [item.guid for item in response]
        return [ObservedDataGrpc(guid, self._plink) for guid in guids]
    
    def GetNumberOfObservedDataObjects(self) -> int:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.ObservedDataSet_GetNumberOfObservedDataObjects(request)
        return response.value

    def GetDates(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        responses = self._channel.ObservedDataSet_GetDates(request)

        dates = []
        for response in responses:
            for date in response.GetDates:
                py_date = datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
                dates.append(py_date)
        return dates
    

    def GetDataFrame(self) -> pd.DataFrame:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)

        responses = self._channel.ObservedDataSet_GetDataFrame(request)
        values = {}
        for response in responses:
            column = response.WhichOneof('column')
            if column == 'dates':
                if 'dates' not in values:
                    values['Date'] = []
                for date in response.dates.values:
                    values['Date'].append(datetime(date.year, date.month, date.day, date.hour, date.minute, date.second))
            elif column == 'data':
                petrel_name = response.data.petrel_name
                if petrel_name not in values:
                    values[petrel_name] = []
                for value in response.data.values:
                    values[petrel_name].append(value)

        df = pd.DataFrame(values)
        return df
    
    def Append(self, date, observedData, values):
        self._plink._opened_test()
        grpc_date = petrelinterface_pb2.Date(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute, second=date.second)
        observedDataGuids = [item._guid for item in observedData]
        observedDataGrpcGuids = [petrelinterface_pb2.PetrelObjectGuid(guid = guid) for guid in observedDataGuids]
        iterable_requests = []
        for index in range(0, len(observedData)):
            request = petrelinterface_pb2.ObservedDataSet_Append_Request(
                guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
                date = grpc_date,
                observedData = observedDataGrpcGuids[index],
                value = values[index]   
            )
            iterable_requests.append(request)
        ok = self._channel.ObservedDataSet_Append((v for v in iterable_requests) )
        return ok.value
    
    def CreateObservedData(self, global_observed_data_id, values):
        self._plink._opened_test()
        iterable_requests = list((petrelinterface_pb2.ObservedDataSet_CreateObservedData_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type), 
            globalObservedDataId = global_observed_data_id,
            values = [v for v in values]
            ) for _ in range(1)
        ))
        created_response = self._channel.ObservedDataSet_CreateObservedData((v for v in iterable_requests) )
        # Force cache to update so that the newly created observed data is added to the cache
        self._plink._find_observed_data() 
        return ObservedDataGrpc(created_response.guid, self._plink)

    def GetParentPythonBoreholeObject(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type)
        response = self._channel.ObservedDataSet_GetParentPythonBoreholeObject(request)
        return borehole_grpc.BoreholeGrpc(response.guid, self._plink)


class GlobalObservedDataSetsGrpc(PetrelObjectGrpc):

    def __init__(self, guid: str, petrel_connection: "PetrelConnection", sub_type: str = 'global observed data set'):
        super(GlobalObservedDataSetsGrpc, self).__init__(sub_type, guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._channel = petrel_connection._service_globalobserveddatasets

    def GetGlobalObservedDataSet(self):
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectRequest(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
        )
        response = self._channel.GetGlobalObservedDataSet(request)
        guid = response.petrel_object_ref.guid
        return GlobalObservedDataSetsGrpc(guid, self._plink)

    def CreateObservedDataSet(self, well):
        self._plink._opened_test()
        request = petrelinterface_pb2.GlobalObservedDataSet_CreateObservedDataSet_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid, sub_type = self._sub_type),
            well = petrelinterface_pb2.PetrelObjectRef(guid = well._petrel_object_link._guid, sub_type = well._petrel_object_link._sub_type)
        )
        response = self._channel.GlobalObservedDataSet_CreateObservedDataSet(request)
        if response.guid:
            return observeddata_grpc.ObservedDataSetGrpc(response.guid, self._plink)
        else:
            return None