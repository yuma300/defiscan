from decimal import Decimal


class TemporaryDeposit:
    def __init__(self):
        self.temporary_deposit = {}

    def push(self, id: str, value: dict):
        self.temporary_deposit[id] = value

    def get(self, id) -> dict:
        return self.temporary_deposit[id]

    def delete(self, id):
        del self.temporary_deposit[id]
