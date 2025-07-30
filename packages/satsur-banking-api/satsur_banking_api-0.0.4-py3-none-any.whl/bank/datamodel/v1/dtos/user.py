from pydantic import EmailStr

from bank.datamodel.v1.dtos.views.usersview import UsersViewDTO


class UserDTO(UsersViewDTO):
    username: str
    password: str
    email: EmailStr

    def __init__(self, **data):
        super().__init__(**data)
