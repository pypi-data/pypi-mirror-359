from datetime import datetime, timedelta

from bank.datamodel.v1.dtos.views.transfersview import TransfersViewDTO


class GetAccountTransfersDTO(TransfersViewDTO):
    account_id: int
    from_time: datetime = datetime.now() - timedelta(days=7)
    to_time: datetime = datetime.now()

    def __init__(self, **data):
        super().__init__(**data)
        self.method = "get_account_transfers"
