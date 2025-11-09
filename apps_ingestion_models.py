from pydantic import BaseModel, HttpUrl
from typing import Optional

class Listing(BaseModel):
    listing_id: str
    title: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]
    price: Optional[int]
    beds: Optional[float]
    baths: Optional[float]
    sqft: Optional[int]
    url: Optional[HttpUrl]
    contact_phone: Optional[str]
    provider: str
    search_id: Optional[str] = None
