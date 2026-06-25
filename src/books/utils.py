
from src.books.models import Book


__all__ = ('find_book_id',)


def find_book_id(book: Book):
    from src.books.router import BOOKS
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
