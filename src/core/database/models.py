# this file is for gathering all models together
# every new app models should import in here for alembic detect

from src.auth.models import User, Permission, RolePermission  # noqa: F401
from src.todo.models import Todo  # noqa: F401
