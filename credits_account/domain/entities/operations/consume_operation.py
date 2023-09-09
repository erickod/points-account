from datetime import date
from typing import List
from uuid import UUID

from credits_account.domain.credit_operations_enum import OperationCreditsEnum
from credits_account.domain.entities import Credit
from credits_account.domain.entities.operations.movement_target import MovementTarget


class ConsumeCreditOperation:
    def __init__(
        self,
        value: int,
        operation_owner_id: UUID,
        description: str = "",
    ) -> None:
        self.value = value
        self.description = description or "Você consumiu créditos"
        self.type = OperationCreditsEnum.CONSUME.name
        self.operation_owner_id = self._validate_operation_owner_id(operation_owner_id)
        self.credits: List[Credit] = []
        self.is_valid()

    def make_credit(
        self,
        reference_date: date,
        account_id: UUID,
    ) -> Credit:
        if self.value > 0:
            self.value = self.value * -1
        return Credit(
            reference_date,
            account_id,
            self.value,
            self.type,
        )

    def set_movement_target(self, target: MovementTarget) -> None:
        self.target = target

    def register_movement(self, credit: Credit) -> None:
        self.credits.append(credit)

    def is_valid(self) -> bool:
        if self.value < 0:
            self.value = self.value * -1
        return True

    def __str__(self) -> str:
        string = f"ConsumeCreditOperation({self.credits})"
        return string

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def _validate_operation_owner_id(id: UUID) -> UUID:
        if type(id) is not UUID:
            raise TypeError(f"Invalid operation_owner_id: {id}")
        return id

    def get_total(self) -> int:
        return self.remaining_value

    @property
    def remaining_value(self) -> int:
        return sum([c.get_consumed_value() for c in self.credits]) * -1
