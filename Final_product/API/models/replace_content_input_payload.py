from typing import Dict, List
from pydantic import BaseModel, RootModel

class Item(BaseModel):
    data: str
    name: str
    path: str
    ext: str

class ReplaceContentInputPayload(RootModel[Dict[str, List[Item]]]):
    pass