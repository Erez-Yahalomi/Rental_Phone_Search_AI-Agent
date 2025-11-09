from pydantic import BaseModel, conint
from typing import Optional, List

class RentalFilters(BaseModel):
    city: str
    state: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    beds: Optional[conint(ge=0)] = None
    baths: Optional[conint(ge=0)] = None
    property_types: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
