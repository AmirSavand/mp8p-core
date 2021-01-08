from typing import Dict, List, Type, Optional, Tuple
from uuid import UUID, uuid4

from flask import jsonify


class Storage:
    LIST: Dict[UUID, "Storage"] = {}

    @staticmethod
    def get(uid: UUID) -> Optional["Storage"]:
        return Storage.LIST.get(uid, None)

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


class ErrorResponse:

    @staticmethod
    def message(message: str) -> Tuple[dict, int]:
        return jsonify({"message": message}), 400

    @staticmethod
    def bad_request() -> Tuple[str, int]:
        return "", 400

    @staticmethod
    def no_player() -> Tuple[str, int]:
        return "", 401

    @staticmethod
    def not_found() -> Tuple[str, int]:
        return "", 404


def get_uuid(value: str) -> Optional[UUID]:
    try:
        return UUID(str(value))
    except ValueError:
        return None


def clamp(value: int, max_value: int, min_value: int = 0) -> int:
    return max(min(value, max_value), min_value)
