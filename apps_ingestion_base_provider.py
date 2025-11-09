from abc import ABC, abstractmethod
from typing import Iterable
from .filters import RentalFilters
from .models import Listing

class ListingProvider(ABC):
    @abstractmethod
    def search(self, filters: RentalFilters, limit: int) -> Iterable[Listing]:
        raise NotImplementedError
