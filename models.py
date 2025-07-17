from pydantic import BaseModel





class Address_Search(BaseModel):
    full_address: str
    latitude: float
    longitude: float
    Valuation: int
