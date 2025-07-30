# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from cegalprizm.pythontool.grpc.petrelinterface_pb2 import PetrelObjectRef, PetrelObjectGuids
from .base_hub import BaseHub

class SurfaceCollectionHub(BaseHub):
    def GetSurfaceCollectionGrpc(self, msg) -> PetrelObjectRef:
        return self._wrapper("cegal.pythontool.GetSurfaceCollectionGrpc", PetrelObjectRef, msg) # type: ignore
    
    def SurfaceCollection_GetRegularHeightFieldObjects(self, msg) -> PetrelObjectGuids:
        return self._unary_wrapper("cegal.pythontool.SurfaceCollection_GetRegularHeightFieldObjects", PetrelObjectGuids, msg) # type: ignore
    