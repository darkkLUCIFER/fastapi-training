from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class CreateTodoSchema(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str | None, Field(min_length=1)] = None
    priority: Annotated[int | None, Field(ge=1, le=5)] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "shop mall",
                "description": "with ali",
                "priority": 2,
            }
        }
    )


class TodoResponseSchema(BaseModel):
    id: int
    title: str
    description: str | None
    priority: int | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
