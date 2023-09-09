from datetime import date
from typing import Optional
from uuid import UUID

from credits_account.domain.credit_operations_enum import OperationCreditsEnum
from credits_account.domain.entities import Credit


class AddCreditOperation:
    def __init__(
        self,
        value: int,
        operation_owner_id: UUID,
        description: str = "",
        credit_type: str = "SUBSCRIPTION",
        contracted_service_id: Optional[UUID] = None,
    ) -> None:
        self.value = value
        self.description = description or "Você adicionou créditos"
        self.type = OperationCreditsEnum.ADD.name
        self.operation_owner_id = self._validate_operation_owner_id(operation_owner_id)
        self.credit: Credit
        self.credit_type = credit_type
        self.contracted_service_id = contracted_service_id

    def make_credit(
        self,
        reference_date: date,
        account_id: UUID,
    ) -> Credit:
        credit = Credit(
            reference_date,
            account_id,
            self.value,
            self.type,
            self.contracted_service_id,
        )
        self.credit = self._validate_credit(credit)
        return self.credit

    @staticmethod
    def _validate_credit(credit: Credit) -> Credit:
        if not isinstance(credit, Credit):
            TypeError("Type not allowed")
        return credit

    @staticmethod
    def _validate_operation_owner_id(id: UUID) -> UUID:
        if type(id) is not UUID:
            raise TypeError(f"Invalid operation_owner_id: {id}")
        return id

    def get_total(self) -> int:
        return self.remaining_value

    @property
    def remaining_value(self) -> int:
        return self.credit.remaining_value
