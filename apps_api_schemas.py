from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    search_id: str
    city: str
    state: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    user_questions: Optional[List[str]] = None

class SearchResponse(BaseModel):
    count: int

class StartCallsRequest(BaseModel):
    search_id: str
    user_questions: Optional[List[str]] = None

class StartCallsResponse(BaseModel):
    scheduled: int
