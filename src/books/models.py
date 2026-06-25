from datetime import datetime


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: datetime

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date
