"""
Book management router: CRUD and list operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas
from .database import get_db
from .routes_auth import get_current_user

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

# PUBLIC_INTERFACE
@router.post("/", summary="Add a new book", response_model=schemas.BookOut)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Create a new book entry (owner is current user)."""
    db_book = models.Book(
        title=book.title,
        author=book.author,
        description=book.description,
        image_url=book.image_url,
        category=book.category,
        owner_id=current_user.id,
        is_for_sale=book.is_for_sale,
        price=book.price if book.is_for_sale else None,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# PUBLIC_INTERFACE
@router.get("/", summary="List all books", response_model=List[schemas.BookOut])
def list_books(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Category filter"),
    search: Optional[str] = Query(None, description="Search by title or author"),
    for_sale: Optional[bool] = Query(None, description="Filter books for sale"),
):
    """Return a list of all books in the marketplace, with optional filters."""
    query = db.query(models.Book).filter(models.Book.is_available.is_(True))
    if category:
        query = query.filter(models.Book.category == category)
    if for_sale is not None:
        query = query.filter(models.Book.is_for_sale == for_sale)
    if search:
        query = query.filter((models.Book.title.ilike(f"%{search}%")) | (models.Book.author.ilike(f"%{search}%")))
    return query.all()

# PUBLIC_INTERFACE
@router.get("/{book_id}", summary="Get a book's details", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Return details for a single book by id."""
    book = db.query(models.Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# PUBLIC_INTERFACE
@router.put("/{book_id}", summary="Update a book (owner only)", response_model=schemas.BookOut)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update an existing book. Only the owner can update."""
    book = db.query(models.Book).get(book_id)
    if not book or book.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Book not found or not authorized")
    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

# PUBLIC_INTERFACE
@router.delete("/{book_id}", summary="Delete a book (owner only)", status_code=204)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a book. Only the owner can delete."""
    book = db.query(models.Book).get(book_id)
    if not book or book.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Book not found or not authorized")
    db.delete(book)
    db.commit()
    return
