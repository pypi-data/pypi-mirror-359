from datetime import datetime
from decimal import Decimal

from bank.datamodel.v1.dtos.views.accountsview import AccountsViewDTO


class BalanceDTO(AccountsViewDTO):
    account_id: int
    amount: Decimal
    last_updated_time: datetime

    def __init__(self, **data):
        super().__init__(**data)
