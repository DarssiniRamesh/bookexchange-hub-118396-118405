"""
SQLAlchemy ORM models for users, books, swaps, and purchases.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Enum,
    Float
)
from sqlalchemy.orm import relationship
import enum

from .database import Base


class SwapStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class PurchaseStatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    books = relationship("Book", back_populates="owner")
    book_swaps = relationship("SwapRequest", back_populates="requester", foreign_keys='SwapRequest.requester_id')
    received_swaps = relationship("SwapRequest", back_populates="book_owner", foreign_keys='SwapRequest.book_owner_id')
    purchases = relationship("Purchase", back_populates="buyer")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    category = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True)
    is_for_sale = Column(Boolean, default=False)
    price = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="books")
    swap_requests = relationship("SwapRequest", back_populates="book")
    purchases = relationship("Purchase", back_populates="book")


class SwapRequest(Base):
    __tablename__ = "swap_requests"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    book_owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(SwapStatusEnum), default=SwapStatusEnum.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    book = relationship("Book", back_populates="swap_requests")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="book_swaps")
    book_owner = relationship("User", foreign_keys=[book_owner_id], back_populates="received_swaps")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    status = Column(Enum(PurchaseStatusEnum), default=PurchaseStatusEnum.pending)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    buyer = relationship("User", back_populates="purchases")
    book = relationship("Book", back_populates="purchases")
