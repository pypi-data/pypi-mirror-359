from bank.datamodel.v1.dtos.views.base import BaseDTO


class TransfersViewDTO(BaseDTO):
    def __init__(self, **data):
        super().__init__(**data)
        self.view = "banking.apps.bank.v1.view.transfersview.TransfersView"
