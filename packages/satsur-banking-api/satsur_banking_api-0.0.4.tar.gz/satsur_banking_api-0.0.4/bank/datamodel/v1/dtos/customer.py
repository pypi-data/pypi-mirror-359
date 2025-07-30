from datetime import datetime

from bank.datamodel.v1.dtos.views.customersview import CustomersViewDTO


class CustomerDTO(CustomersViewDTO):
    id: int
    name: str
    creation_time: datetime

    def __init__(self, **data):
        super().__init__(**data)
