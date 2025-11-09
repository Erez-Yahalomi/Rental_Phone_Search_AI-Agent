from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, ForeignKey, JSON, Text
from typing import Optional, Dict, List

Base = declarative_base()

class ListingORM(Base):
    __tablename__ = "listings"

    listing_id: Mapped[str] = mapped_column(String, primary_key=True)
    provider: Mapped[str] = mapped_column(String, index=True)
    search_id: Mapped[Optional[str]] = mapped_column(String, index=True)

    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    zipcode: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    beds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    baths: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sqft: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    conversations: Mapped[List["ConversationORM"]] = relationship("ConversationORM", back_populates="listing")

class ConversationORM(Base):
    __tablename__ = "conversations"

    call_sid: Mapped[str] = mapped_column(String, primary_key=True)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.listing_id"), index=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    answers: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    questions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    listing: Mapped["ListingORM"] = relationship("ListingORM", back_populates="conversations")
