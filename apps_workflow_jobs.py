from dataclasses import dataclass
from typing import List

@dataclass
class CallJob:
    listing_id: str
    to_number: str
    questions: List[str]
    search_id: str
