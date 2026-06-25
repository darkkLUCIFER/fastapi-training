from datetime import datetime
from typing import Optional, Annotated

from fastapi import APIRouter, Query, HTTPException

from src.books.models import Book
from src.books.schema import BookRequest
from src.books.utils import find_book_id
from src.books.constants import messages


router = APIRouter()

BOOKS = [
    Book(1, 'Computer Science', "mahdi", "good book", 5, datetime(2020, 10, 12)),
    Book(2, 'be fast with fast api', "mahdi", "great book", 4, datetime(2021, 4, 24)),
    Book(3, 'master endpoint', "mahdi", "awesome book", 2, datetime(2018, 8, 12)),
    Book(4, 'HP1', "ali", "nice and good book", 3, datetime(2012, 4, 13)),
    Book(5, 'HP2', "javad", "good & useful book", 1, datetime(2012, 4, 14)),
    Book(5, 'HP3', "javad", "good & useful book", 2, datetime(2012, 4, 15)),
]


@router.get("/books")
async def read_all_books(rating: Annotated[Optional[int], Query(ge=0, le=5)] = None):
    if rating is not None:
        return [book for book in BOOKS if book.rating == rating]

    return BOOKS


@router.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail=messages.BOOK_NOT_FOUND)


@router.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            BOOKS.remove(book)
    raise HTTPException(status_code=404, detail=messages.BOOK_NOT_FOUND)


@router.put("/books/{book_id}/update_book/")
async def update_book(book_id: int, updated_book: BookRequest):
    for book in BOOKS:
        if book.id == book_id:
            book.title = updated_book.title
            book.author = updated_book.author
            book.description = updated_book.description
            book.rating = updated_book.rating
            book.published_date = updated_book.published_date

            return book
    raise HTTPException(status_code=404, detail=messages.BOOK_NOT_FOUND)


@router.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    created_book = find_book_id(new_book)
    BOOKS.append(find_book_id(new_book))
    return created_book
