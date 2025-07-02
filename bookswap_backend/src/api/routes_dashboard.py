"""
User dashboard/history router for books, swaps, purchases.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .routes_auth import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# PUBLIC_INTERFACE
@router.get("/", response_model=schemas.UserHistory, summary="User dashboard/history overview")
def get_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all books, swaps, and purchases for the current user."""
    books = db.query(models.Book).filter(models.Book.owner_id == current_user.id).all()
    swaps = db.query(models.SwapRequest).filter(
        (models.SwapRequest.requester_id == current_user.id)
        | (models.SwapRequest.book_owner_id == current_user.id)
    ).all()
    purchases = db.query(models.Purchase).filter(models.Purchase.buyer_id == current_user.id).all()
    return schemas.UserHistory(books=books, swaps=swaps, purchases=purchases)
