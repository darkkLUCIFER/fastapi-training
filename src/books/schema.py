from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Optional


class BookRequest(BaseModel):
    id: Optional[Annotated[int, Field(title='id is not needed')]] = None
    title: Annotated[str, Field(min_length=3)]
    author: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1, max_length=100)]
    rating: Annotated[int, Field(ge=0, le=5)]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "A New Book",
                "author": "sorena",
                "description": "A New Description for Book",
                "rating": 5
            }
        }
    )
