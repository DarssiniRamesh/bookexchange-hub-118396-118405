from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routes_auth import router as auth_router
from .routes_books import router as book_router
from .routes_swaps import router as swap_router
from .routes_purchases import router as purchase_router
from .routes_dashboard import router as dashboard_router

app = FastAPI(
    title="Book Exchange Hub API",
    description="API for book swapping, marketplace, user profiles, swaps, and purchases.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

# Create DB tables at startup (for dev - switch to alembic migrations later)
@app.on_event("startup")
def create_tables():
    models.Base.metadata.create_all(bind=engine)

# Mount all routers
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(swap_router)
app.include_router(purchase_router)
app.include_router(dashboard_router)
