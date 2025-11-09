 
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from apps.ingestion.factory import create_provider
from apps.storage.repositories import ListingRepository
from config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    search_id: str
    city: Optional[str] = None
    state: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    user_questions: Optional[list] = None

class SearchResponse(BaseModel):
    search_id: str
    results_count: int

@router.post("/search", response_model=SearchResponse)
def search_listings(req: SearchRequest):
    """
    Ingest listings using the configured provider adapter returned by create_provider().
    """
    provider = create_provider()
    logger.info("Using listing provider: %s", settings.LISTING_PROVIDER)
    listings = provider.search_listings(
        city=(req.city or ""),
        state=(req.state or ""),
        min_price=(req.min_price or 0),
        max_price=(req.max_price or 0),
        beds=(req.beds or 0),
        baths=(req.baths or 0),
        limit=settings.MAX_LISTINGS_PER_SEARCH
    )

    if not listings:
        raise HTTPException(status_code=404, detail="No listings found")

    # attach search_id and persist
    repo = ListingRepository()
    for l in listings:
        l["search_id"] = req.search_id
    repo.upsert_many(listings)

    return SearchResponse(search_id=req.search_id, results_count=len(listings))
