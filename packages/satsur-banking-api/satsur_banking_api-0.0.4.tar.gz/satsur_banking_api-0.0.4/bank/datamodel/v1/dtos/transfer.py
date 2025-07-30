from datetime import datetime
from decimal import Decimal

from bank.datamodel.v1.dtos.views.transfersview import TransfersViewDTO


class TransferDTO(TransfersViewDTO):
    from_account_id: int
    to_account_id: int
    amount: Decimal
    time: datetime

    def __init__(self, **data):
        super().__init__(**data)
