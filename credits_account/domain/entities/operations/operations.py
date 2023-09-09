from dataclasses import dataclass
from datetime import date
from typing import Any, List
from uuid import UUID

from credits_account.domain.credit_operations_enum import OperationCreditsEnum
from credits_account.domain.entities.credit import Credit
from credits_account.domain.entities.operations.add_operation import AddCreditOperation
from credits_account.domain.entities.operations.movement_target import MovementTarget


class ExpireCreditOperation:
    def __init__(
        self, operation_owner_id: UUID, description="Seus créditos expiraram"
    ) -> None:
        self.credits = []
        self.description = description
        self.type = OperationCreditsEnum.EXPIRE.name
        self.operation_owner_id = operation_owner_id

    def register_movement(self, credit: Credit) -> None:
        if credit in self.credits:
            return
        self.credits.append(credit)

    def __eq__(self, other: Any) -> bool:
        if type(other) != type(self):
            return False
        return self.credits == other.credits


class RefundCreditOperation:
    def __init__(
        self,
        operation_owner_id: UUID,
        company_id: UUID,
        object_type: str,
        object_id: str,
    ) -> None:
        self.credits: List[Credit] = []
        self.description = "Seus créditos foram estornados"
        self.type = OperationCreditsEnum.REFUND.name
        self.operation_owner_id = operation_owner_id
        self.target: MovementTarget = MovementTarget(object_type, object_id)
        self.company_id = company_id

    def __eq__(self, other: Any) -> bool:
        if type(other) != type(self):
            return False
        return all(
            [
                self.target == other.target,
                # self.credits == other.credits
            ]
        )

    def register_movement(self, credit: Credit) -> None:
        self.credits.append(credit)

    property

    def consumed_value(self) -> int:
        return sum([credit.consumed_value for credit in self.credits])


class RenewCreditOperation:
    def __init__(self, operation_owner_id: UUID, *credits: List[Credit]) -> None:
        self.operation_owner_id = operation_owner_id
        self.type = OperationCreditsEnum.RENEW.name
        self.credits_to_add = []
        self.register_movement(credits)

    def add_operation_factory(self) -> AddCreditOperation:
        return AddCreditOperation(
            self.operation_owner_id, "Renovação de assinatura", *self.credits_to_add
        )

    def expire_operation_factory(self) -> ExpireCreditOperation:
        return ExpireCreditOperation(self.operation_owner_id)

    def register_movement(self, credits: List[Credit]) -> None:
        for credit in credits:
            if (
                credit.is_expired(reference_date=date.today())
                and credit.contract_service_id
            ):
                self.credits_to_add.append(credit)
