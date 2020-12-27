from typing import Dict, List, Type
from uuid import UUID, uuid4


class Storage:
    LIST: Dict[UUID, "Storage"] = {}

    @staticmethod
    def get(uid: UUID) -> "Storage":
        return Storage.LIST[uid]

    @staticmethod
    def list(class_match: Type["Storage"]) -> List["Storage"]:
        output: List[Storage] = []
        for item in Storage.LIST.values():
            if item.__class__ is class_match:
                output.append(item)
        return output

    def __init__(self) -> None:
        self.uid = uuid4()
        self.LIST[self.uid] = self

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.uid}"
