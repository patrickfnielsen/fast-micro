from fast_micro.utils import camelize
from pydantic import BaseModel


class CamelCaseModel(BaseModel):
    class Config:
        alias_generator = camelize
        populate_by_name = True
        frozen = True
