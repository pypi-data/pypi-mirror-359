# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from .petrelobject_grpc import PetrelObjectGrpc
from cegalprizm.pythontool.grpc import petrelinterface_pb2, utils
import datetime
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.petrelconnection import PetrelConnection
    from cegalprizm.pythontool.oophub.completionsset_hub import CompletionsSetHub

class PlugbackGrpc(PetrelObjectGrpc):
    def __init__(self, guid: str, petrel_connection: "PetrelConnection"):
        super(PlugbackGrpc, self).__init__('plugback', guid, petrel_connection)
        self._guid = guid
        self._plink = petrel_connection
        self._invariant_content = {}
        self._channel = typing.cast("CompletionsSetHub", petrel_connection._service_completionsset)

    def GetTopMd(self) -> float:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPlugbackTopMd(request)
        return response.Md
    
    def SetTopMd(self, new_top_md: float) -> bool:
        self._plink._opened_test()
        request = petrelinterface_pb2.CompletionsSet_SetDepth_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewMd = new_top_md
        )
        response = self._channel.SetPlugbackTopMd(request)
        return response.value
    
    def GetBottomMd(self) -> float:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPlugbackBottomMd(request)
        return response.Md
    
    def GetStartDate(self) -> datetime.datetime:
        self._plink._opened_test()
        request = petrelinterface_pb2.PetrelObjectGuid(
            guid = self._guid
        )
        response = self._channel.GetPlugbackStartDate(request)
        grpcDate: petrelinterface_pb2.Date = response.Date
        date = datetime.datetime(grpcDate.year, grpcDate.month, grpcDate.day, grpcDate.hour, grpcDate.minute, grpcDate.second)
        return date
    
    def SetStartDate(self, new_start_date: datetime.datetime) -> bool:
        self._plink._opened_test()
        grpcDate = utils.datetime_to_pb_date(new_start_date)
        request = petrelinterface_pb2.PetrelObject_SetDate_Request(
            guid = petrelinterface_pb2.PetrelObjectGuid(guid = self._guid),
            NewDate = grpcDate
        )
        response = self._channel.SetPlugbackStartDate(request)
        return response.value