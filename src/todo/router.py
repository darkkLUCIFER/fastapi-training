from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Path
from starlette import status

from src.todo.dependencies import get_todo_service
from src.todo.schema import CreateTodoSchema, TodoResponseSchema, UpdateTodoSchema
from src.todo.services import TodoService


router = APIRouter()


@router.post(
    "/", response_model=TodoResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_todo(
    data: CreateTodoSchema,
    background_tasks: BackgroundTasks,
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    return service.create(data, background_tasks)


@router.get(
    "/", response_model=list[TodoResponseSchema], status_code=status.HTTP_200_OK
)
def list_todos(
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    return service.get_all()


@router.get(
    "/{todo_id}", response_model=TodoResponseSchema, status_code=status.HTTP_200_OK
)
def get_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    return service.get_one(todo_id=todo_id)


@router.patch(
    "/{todo_id}", response_model=TodoResponseSchema, status_code=status.HTTP_200_OK
)
def update_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
    data: UpdateTodoSchema,
):
    return service.update_one(todo_id=todo_id, data=data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
):
    return service.delete_one(todo_id=todo_id)
