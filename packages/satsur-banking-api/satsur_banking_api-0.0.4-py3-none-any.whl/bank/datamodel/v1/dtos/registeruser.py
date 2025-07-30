from pydantic import EmailStr, model_validator
from typing_extensions import Self

from bank.datamodel.v1.dtos.views.usersview import UsersViewDTO


class RegisterUserDTO(UsersViewDTO):
    username: str
    password: str
    email: EmailStr

    def __init__(self, **data):
        super().__init__(**data)
        self.method = "register_user"

    @model_validator(mode="after")
    def validate_create_user(self) -> Self:
        if not len(self.username.strip()) >= 6:
            raise AssertionError("Username must be at least 6 characters")

        if not len(self.password.strip()) >= 10:
            raise AssertionError("Password must be at least 10 characters")

        return self
