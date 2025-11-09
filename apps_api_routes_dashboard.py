from fastapi import APIRouter
from apps.storage.repositories import ConversationRepository

router = APIRouter()

@router.get("/summaries")
def list_summaries(search_id: str):
    """
    Return summaries + listing details for dashboard.
    """
    repo = ConversationRepository()
    items = repo.list_summaries(search_id)
    return {"items": items}
