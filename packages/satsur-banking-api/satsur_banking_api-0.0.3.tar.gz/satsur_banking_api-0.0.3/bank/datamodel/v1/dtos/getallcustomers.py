from datetime import datetime, timedelta

from bank.datamodel.v1.dtos.views.customersview import CustomersViewDTO


class GetAllCustomersDTO(CustomersViewDTO):
    from_time: datetime = datetime.now() - timedelta(days=7)
    to_time: datetime = datetime.now()

    def __init__(self, **data):
        super().__init__(**data)
        self.method = "get_all_customers"
