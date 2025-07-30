from typing import Dict, Any, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar("T", bound="BaseModel")


class BaseModel(ABC):

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        pass

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if hasattr(value, "to_dict"):
                    result[key] = value.to_dict()
                elif isinstance(value, list):
                    result[key] = [
                        item.to_dict() if hasattr(item, "to_dict") else item
                        for item in value
                    ]
                else:
                    result[key] = value
        return result

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
