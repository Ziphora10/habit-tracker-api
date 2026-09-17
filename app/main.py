from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, habits

# Import models so they are registered on Base before create_all is called.
from app.models import habit, user  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router)
app.include_router(habits.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
