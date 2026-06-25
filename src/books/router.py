from fastapi import APIRouter

from src.books.models import Book
from src.books.schema import BookRequest
from src.books.utils import find_book_id


router = APIRouter()

BOOKS = [
    Book(1, 'Computer Science', "mahdi", "good book", 5),
    Book(2, 'be fast with fast api', "mahdi", "great book", 4),
    Book(3, 'master endpoint', "mahdi", "awesome book", 2),
    Book(4, 'HP1', "ali", "nice and good book", 3),
    Book(5, 'HP2', "javad", "good & useful book", 1),
]


@router.get("/books")
async def read_all_books():
    return BOOKS


@router.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book


@router.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    created_book = find_book_id(new_book)
    BOOKS.append(find_book_id(new_book))
    return created_book
