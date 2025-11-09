from fastapi import APIRouter
from apps.api.schemas import SearchRequest, SearchResponse
from apps.ingestion.filters import RentalFilters
from apps.ingestion.rentpath_provider import RentPathProvider
from apps.storage.repositories import ListingRepository
from config.settings import settings

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_listings(req: SearchRequest):
    """
    Fetch listings from RentPath and store them with the given search_id.
    """
    filters = RentalFilters(
        city=req.city,
        state=req.state,
        min_price=req.min_price,
        max_price=req.max_price,
        beds=req.beds,
        baths=req.baths,
        property_types=None,
        keywords=None,
    )
    provider = RentPathProvider()
    listings = []
    for listing in provider.search(filters, limit=settings.MAX_LISTINGS_PER_SEARCH):
        d = listing.dict()
        d["search_id"] = req.search_id
        listings.append(d)

    repo = ListingRepository()
    repo.upsert_many(listings)
    return SearchResponse(count=len(listings))
