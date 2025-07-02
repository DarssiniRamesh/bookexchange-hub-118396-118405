"""
Swap request router: initiate, accept/reject, list, user history.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import get_db
from .routes_auth import get_current_user

router = APIRouter(
    prefix="/swaps",
    tags=["Swaps"]
)

# PUBLIC_INTERFACE
@router.post("/", summary="Request a book swap", response_model=schemas.SwapRequestOut)
def request_swap(swap_in: schemas.SwapRequestIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Request to swap (send request to book owner for their book)."""
    book = db.query(models.Book).get(swap_in.book_id)
    if not book or not book.is_available:
        raise HTTPException(status_code=404, detail="Book unavailable")
    if book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot swap own book")
    swap = models.SwapRequest(
        book_id=book.id,
        requester_id=current_user.id,
        book_owner_id=book.owner_id,
        status=schemas.SwapStatusEnum.pending
    )
    db.add(swap)
    db.commit()
    db.refresh(swap)
    return swap

# PUBLIC_INTERFACE
@router.get("/", summary="List all swap requests (admin)", response_model=List[schemas.SwapRequestOut])
def list_swaps(db: Session = Depends(get_db)):
    """List all swap requests (admin use)."""
    return db.query(models.SwapRequest).all()

# PUBLIC_INTERFACE
@router.get("/my", summary="My outgoing swap requests", response_model=List[schemas.SwapRequestOut])
def my_swaps(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """View swap requests made by the user."""
    return db.query(models.SwapRequest).filter(models.SwapRequest.requester_id == current_user.id).all()

# PUBLIC_INTERFACE
@router.get("/received", summary="My received swap requests", response_model=List[schemas.SwapRequestOut])
def received_swaps(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """View swap requests received by the current user (as book owner)."""
    return db.query(models.SwapRequest).filter(models.SwapRequest.book_owner_id == current_user.id).all()

# PUBLIC_INTERFACE
@router.put(
    "/{swap_id}/status",
    summary="Update swap status",
    response_model=schemas.SwapRequestOut
)
def update_swap_status(
    swap_id: int,
    status_update: schemas.SwapRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Accept or reject/cancel a swap request (only owner or requester can update)."""
    swap = db.query(models.SwapRequest).get(swap_id)
    if not swap:
        raise HTTPException(status_code=404, detail="Swap request not found")
    if status_update.status == schemas.SwapStatusEnum.accepted:
        if swap.book_owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only book owner can accept swap")
        swap.status = schemas.SwapStatusEnum.accepted
        swap.book.is_available = False
    elif status_update.status == schemas.SwapStatusEnum.rejected:
        if swap.book_owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only book owner can reject swap")
        swap.status = schemas.SwapStatusEnum.rejected
    elif status_update.status == schemas.SwapStatusEnum.cancelled:
        if swap.requester_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only requester can cancel swap")
        swap.status = schemas.SwapStatusEnum.cancelled
    else:
        raise HTTPException(status_code=400, detail="Invalid status update")
    db.commit()
    db.refresh(swap)
    return swap
