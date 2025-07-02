"""
Purchase router: initiate purchase, list user purchases, Stripe stub.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import get_db
from .routes_auth import get_current_user

router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"]
)

# PUBLIC_INTERFACE
@router.post("/", summary="Make a book purchase (Stripe stubbed)", response_model=schemas.PurchaseOut)
def create_purchase(purchase_req: schemas.PurchaseRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Initiate a purchase. Stripe is not fully integrated - this is a stub."""
    book = db.query(models.Book).get(purchase_req.book_id)
    if not book or not book.is_for_sale or not book.is_available:
        raise HTTPException(status_code=404, detail="Book not for sale or unavailable")
    if book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot purchase own book")

    # Stripe integration would happen here: create payment intent, etc.
    # For now, simulate as if payment succeeded instantly.
    purchase = models.Purchase(
        buyer_id=current_user.id,
        book_id=book.id,
        amount=purchase_req.amount,
        status=schemas.PurchaseStatusEnum.completed,
        stripe_payment_intent_id="stubbed-intent-id",
    )
    book.is_available = False
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase

# PUBLIC_INTERFACE
@router.get("/my", summary="My purchases", response_model=List[schemas.PurchaseOut])
def get_my_purchases(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Return all purchases for the current user."""
    return db.query(models.Purchase).filter(models.Purchase.buyer_id == current_user.id).all()
