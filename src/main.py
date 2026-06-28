import logging

from fastapi import FastAPI
from src.books import router as books_router
from src.todo import router as todos_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI()

app.include_router(books_router.router, tags=['books'])
app.include_router(todos_router.router, tags=['todos'], prefix="/todo")
