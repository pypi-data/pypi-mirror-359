# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import typing
from cegalprizm.pythontool import PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.grpc.interpretation_collection_grpc import InterpretationCollectionGrpc

class InterpretationFolder(PetrelObject, PetrelObjectWithTemplateToBeDeprecated, PetrelObjectWithHistoryToBeDeprecated, PetrelObjectWithPetrelNameSetter):
    """A class holding information about an interpretation folder (InterpretationCollection)."""

    def __init__(self, petrel_object_link: "InterpretationCollectionGrpc"):
        super(InterpretationFolder, self).__init__(petrel_object_link)
        self._interpretation_collection_object_link = petrel_object_link
    
    def __str__(self) -> str:
        """A readable representation"""
        return 'InterpretationFolder(petrel_name="{0}")'.format(self.petrel_name)