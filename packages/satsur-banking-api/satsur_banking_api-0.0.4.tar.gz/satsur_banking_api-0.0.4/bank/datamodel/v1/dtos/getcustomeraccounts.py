from bank.datamodel.v1.dtos.views.accountsview import AccountsViewDTO


class GetCustomerAccountsDTO(AccountsViewDTO):
    customer_id: int

    def __init__(self, **data):
        super().__init__(**data)
        self.method = "get_customer_accounts"
