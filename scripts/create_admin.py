import getpass
import sys

from pydantic import ValidationError

from src.auth.constants import RoleChoices
from src.auth.schema import RegisterSuperUserSchema
from src.auth.services import AuthService
from src.auth.uow import AuthUow
from src.core import SecurityUtils, SessionLocal


def create_admin_user_cli() -> None:
    """
        this script handles creating admin user with command line interface with make
    :return: None
    """
    print("--- Create Admin User ---")

    try:
        username = input("Enter Username: ").strip()
        email = input("Enter Email: ").strip()

        password = getpass.getpass("Enter Password: ")
        password_confirmation = getpass.getpass("Confirm Password: ")

        data = {
            "username": username,
            "email": email,
            "password": password,
            "password_confirmation": password_confirmation,
            "role": RoleChoices.ADMIN.value,
        }

        register_data = RegisterSuperUserSchema.model_validate(data)

        with SessionLocal() as db:
            service = AuthService(
                uow=AuthUow(db),
                security=SecurityUtils(),
            )

            service.register_user(data=register_data)

        print("Admin user created successfully.")

    except ValidationError as exc:
        print("Invalid input:")

        for error in exc.errors():
            location = " -> ".join(str(item) for item in error["loc"])
            print(f"  {location}: {error['msg']}")

        sys.exit(1)

    except Exception as exc:
        print(f"An error occurred while creating admin user: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    create_admin_user_cli()
