from typing import Dict, List, Optional
from .db import SessionLocal
from .orm_models import Base, ListingORM, ConversationORM
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class ListingRepository:
    def __init__(self):
        self.db = SessionLocal()

    def create_tables(self):
        Base.metadata.create_all(bind=self.db.get_bind())

    def upsert_many(self, listings: List[Dict]) -> None:
        try:
            for l in listings:
                listing_id = l.get("listing_id")
                if not listing_id:
                    continue
                obj = self.db.get(ListingORM, listing_id)
                if obj:
                    for k, v in l.items():
                        if hasattr(obj, k):
                            setattr(obj, k, v)
                else:
                    obj = ListingORM(**l)
                    self.db.add(obj)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            logger.exception("IntegrityError while upserting listings")
            raise

    def list_by_search_id(self, search_id: str) -> List[Dict]:
        res = self.db.execute(select(ListingORM).where(ListingORM.search_id == search_id)).scalars().all()
        return [self._to_dict(x) for x in res]

    def get_by_id(self, listing_id: str) -> Optional[ListingORM]:
        return self.db.get(ListingORM, listing_id)

    def _to_dict(self, obj: ListingORM) -> Dict:
        return {
            "listing_id": obj.listing_id,
            "provider": obj.provider,
            "search_id": obj.search_id,
            "title": obj.title,
            "address": obj.address,
            "city": obj.city,
            "state": obj.state,
            "zipcode": obj.zipcode,
            "price": obj.price,
            "beds": obj.beds,
            "baths": obj.baths,
            "sqft": obj.sqft,
            "url": obj.url,
            "contact_phone": obj.contact_phone,
        }


class ConversationRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_or_create(self, call_sid: Optional[str], listing_id: str) -> ConversationORM:
        """
        If call_sid exists, return that conversation. Otherwise create a placeholder
        conversation keyed by a temporary SID and ensure listing_id is stored.
        """
        if call_sid:
            obj = self.db.get(ConversationORM, call_sid)
            if obj:
                return obj

        temp_sid = call_sid or f"pending-{listing_id}"
        obj = self.db.get(ConversationORM, temp_sid)
        if not obj:
            obj = ConversationORM(call_sid=temp_sid, listing_id=listing_id, state="INTRO", answers={}, questions=[])
            self.db.add(obj)
            self.db.commit()
            logger.info("Created new conversation placeholder %s for listing %s", temp_sid, listing_id)
        return obj

    def attach_questions(self, call_sid: str, questions: List[str]):
        obj = self.db.get(ConversationORM, call_sid)
        if obj:
            obj.questions = questions
            self.db.commit()
            logger.debug("Attached %d questions to conversation %s", len(questions), call_sid)
        else:
            logger.warning("attach_questions: conversation %s not found", call_sid)

    def update(self, call_sid: str, state: str, answers: Dict[str, str]):
        obj = self.db.get(ConversationORM, call_sid)
        if not obj:
            obj = ConversationORM(call_sid=call_sid, listing_id="", state=state, answers=answers, questions=[])
            self.db.add(obj)
            self.db.commit()
            logger.info("Created conversation record on update for call_sid %s", call_sid)
            return
        obj.state = state
        obj.answers = answers
        self.db.commit()
        logger.debug("Updated conversation %s state=%s", call_sid, state)

    def save_summary(self, call_sid: str, summary: str):
        obj = self.db.get(ConversationORM, call_sid)
        if obj:
            obj.summary_text = summary
            self.db.commit()
            logger.info("Saved summary for conversation %s", call_sid)
        else:
            logger.warning("save_summary: conversation %s not found", call_sid)

    def list_summaries(self, search_id: str) -> List[Dict]:
        stmt = select(ConversationORM, ListingORM).join(ListingORM, ConversationORM.listing_id == ListingORM.listing_id)\
            .where(ListingORM.search_id == search_id)
        rows = self.db.execute(stmt).all()
        items = []
        for convo, listing in rows:
            items.append({
                "listing_id": listing.listing_id,
                "listing_details": {
                    "title": listing.title,
                    "address": listing.address,
                    "city": listing.city,
                    "state": listing.state,
                    "zipcode": listing.zipcode,
                    "price": listing.price,
                    "beds": listing.beds,
                    "baths": listing.baths,
                    "sqft": listing.sqft,
                    "url": listing.url,
                },
                "summary_text": convo.summary_text or "",
            })
        return items
