from fastapi import FastAPI
from src.books import router as books_router

app = FastAPI()

app.include_router(books_router.router, tags=["books"])
