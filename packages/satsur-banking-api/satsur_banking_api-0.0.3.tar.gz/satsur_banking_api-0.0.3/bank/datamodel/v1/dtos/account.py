from datetime import datetime

from bank.datamodel.v1.dtos.views.accountsview import AccountsViewDTO


class AccountDTO(AccountsViewDTO):
    id: int
    customer_id: int
    creation_time: datetime

    def __init__(self, **data):
        super().__init__(**data)
