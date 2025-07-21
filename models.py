from pydantic import BaseModel
from typing import Optional





class Address_Search(BaseModel):
    full_address: str
    latitude: float
    longitude: float
    Valuation: int

class Attribute(BaseModel):
    Location: str
    OBJECTID: str
    Shape: str
    Valuation_No: str
    Title_Prefix: str
    Title_Volume: str
    Title_Folio: str
class Coordinate_Search(BaseModel):
    layerId: Optional[int] = None
    layerName: Optional[str] = None
    displayFieldName: Optional[str] = None
    value: Optional[str] = None
    attributes: Optional[Attribute] = None