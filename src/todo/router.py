from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette import status

from src.todo.dependencies import get_todo_service
from src.todo.schema import CreateTodoSchema, TodoResponseSchema
from src.todo.services import TodoService


router = APIRouter()


@router.post("/", response_model=TodoResponseSchema, status_code=status.HTTP_201_CREATED)
def create_todo(
    data: CreateTodoSchema,
    background_tasks: BackgroundTasks,
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    return service.create(data, background_tasks)
