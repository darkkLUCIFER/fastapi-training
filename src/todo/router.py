from typing import Annotated

from fastapi import Path, Depends, APIRouter, BackgroundTasks
from starlette import status

from src.auth.models import User
from src.todo.schema import CreateTodoSchema, UpdateTodoSchema, TodoResponseSchema
from src.todo.services import TodoService
from src.auth.dependencies import get_current_user
from src.todo.dependencies import get_todo_service


router = APIRouter()


@router.post(
    '/',
    response_model=TodoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new todo',
    description='Create a new todo item with title, description, and priority.',
)
def create_todo(
    data: CreateTodoSchema,
    background_tasks: BackgroundTasks,
    service: Annotated[TodoService, Depends(get_todo_service)],
    user: Annotated[User, Depends(get_current_user)],
):
    return service.create(data, background_tasks, user)


@router.get(
    '/',
    response_model=list[TodoResponseSchema],
    status_code=status.HTTP_200_OK,
    summary='List all todos',
    description='Retrieve a list of all todo items.',
)
def list_todos(
    service: Annotated[TodoService, Depends(get_todo_service)],
    user: Annotated[User, Depends(get_current_user)],
):
    return service.get_all(user)


@router.get(
    '/{todo_id}/',
    response_model=TodoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Get a todo by ID',
    description='Retrieve a single todo item by its ID.',
)
def get_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
    user: Annotated[User, Depends(get_current_user)],
):
    return service.get_one(todo_id=todo_id, user=user)


@router.patch(
    '/{todo_id}/',
    response_model=TodoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Update a todo',
    description='Update a todo item. Only provided fields will be updated.',
)
def update_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
    data: UpdateTodoSchema,
    user: Annotated[User, Depends(get_current_user)],
):
    return service.update_one(todo_id=todo_id, data=data, user=user)


@router.delete(
    '/{todo_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete a todo',
    description='Delete a todo item by its ID.',
)
def delete_todo(
    todo_id: Annotated[int, Path(ge=1)],
    service: Annotated[TodoService, Depends(get_todo_service)],
    user: Annotated[User, Depends(get_current_user)],
):
    return service.delete_one(todo_id=todo_id, user=user)
