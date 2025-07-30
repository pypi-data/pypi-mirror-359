from typing import Generic, TypeVar, Optional

try:
    from pydantic import BaseModel
except ImportError:
    from pydantic.generics import GenericModel as BaseModel

DataT = TypeVar("DataT")

class ResponseModel(BaseModel, Generic[DataT]):
    status: bool
    code: int
    message: str
    data: Optional[DataT] = None
