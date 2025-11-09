import requests
from typing import Iterable
from .base_provider import ListingProvider
from .filters import RentalFilters
from .models import Listing
from config.settings import settings

class RentPathProvider(ListingProvider):
    """
    Provider using RentPath partner API. This example assumes a generic /listings endpoint.
    Adjust fields and paths to your contract. Includes contact_phone necessary for calls.
    """

    def __init__(self):
        self.base_url = settings.RENTPATH_BASE_URL
        self.api_key = settings.RENTPATH_API_KEY

    def search(self, filters: RentalFilters, limit: int) -> Iterable[Listing]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "city": filters.city,
            "state": filters.state,
            "min_price": filters.min_price,
            "max_price": filters.max_price,
            "beds": filters.beds,
            "baths": filters.baths,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        resp = requests.get(f"{self.base_url}/listings", headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("results", []):
            yield Listing(
                listing_id=str(item.get("id")),
                title=item.get("title"),
                address=(item.get("address") or {}).get("line1"),
                city=(item.get("address") or {}).get("city"),
                state=(item.get("address") or {}).get("state"),
                zipcode=(item.get("address") or {}).get("zip"),
                price=item.get("price"),
                beds=item.get("beds"),
                baths=item.get("baths"),
                sqft=item.get("sqft"),
                url=item.get("url"),
                contact_phone=(item.get("contact") or {}).get("phone"),
                provider="rentpath",
            )
