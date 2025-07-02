"""
Pydantic models for API request and response bodies.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class SwapStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class PurchaseStatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# --- Auth ---
class UserSignup(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email")
    password: str = Field(..., min_length=6, description="Password")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Book ---
class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class BookCreate(BookBase):
    is_for_sale: bool = False
    price: Optional[float] = None


class BookUpdate(BookBase):
    is_available: Optional[bool]
    is_for_sale: Optional[bool]
    price: Optional[float]


class BookOut(BookBase):
    id: int
    owner_id: int
    is_available: bool
    is_for_sale: bool
    price: Optional[float]

    class Config:
        orm_mode = True


# --- Swaps ---
class SwapRequestIn(BaseModel):
    book_id: int
    owner_id: int


class SwapRequestStatusUpdate(BaseModel):
    status: SwapStatusEnum = Field(..., description="New status for the swap request")


class SwapRequestOut(BaseModel):
    id: int
    book_id: int
    requester_id: int
    book_owner_id: int
    status: SwapStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# --- Purchase ---
class PurchaseRequest(BaseModel):
    book_id: int
    amount: float


class PurchaseOut(BaseModel):
    id: int
    buyer_id: int
    book_id: int
    status: PurchaseStatusEnum
    stripe_payment_intent_id: Optional[str] = None
    amount: float
    purchased_at: datetime

    class Config:
        orm_mode = True


# --- Dashboard/History ---
class UserHistory(BaseModel):
    books: List[BookOut]
    swaps: List[SwapRequestOut]
    purchases: List[PurchaseOut]
