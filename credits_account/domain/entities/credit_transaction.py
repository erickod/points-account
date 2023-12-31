import uuid
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple, Union

from credits_account.domain.entities.credit_movement import (
    AddCreditMovement,
    ConsumeCreditMovement,
    ExpireCreditMovement,
    RefundCreditMovement,
    RenewCreditMovement,
)

SupportedMovements = Union[
    AddCreditMovement,
    ConsumeCreditMovement,
    ExpireCreditMovement,
    RefundCreditMovement,
    RenewCreditMovement,
]


@dataclass
class CreditTransaction:
    creation_date: date
    account_id: uuid.UUID
    type: str
    contract_service_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None
    contract_service_creation_date: Optional[date] = None

    def __post_init__(self) -> None:
        self.contract_service_creation_date = (
            self.contract_service_creation_date or self.creation_date
        )
        self._usage_list: List[SupportedMovements] = []
        if not self.creation_date:
            self.creation_date = date.today()

    def add(self, value: int, description: str) -> None:
        self.register_movement(
            AddCreditMovement(
                value,
                description,
                None,
                None,
            )
        )

    def consume(
        self,
        value: int,
        *,
        ignore_is_expired_check: bool = False,
        reference_date=date.today(),
        object_type: str = "",
        object_id: str = "",
        description: str = "Você consumiu créditos",
    ) -> int:
        assert value >= 0, "The consume credit value should be greater than 0"
        if self.is_expired(reference_date) and not ignore_is_expired_check:
            raise ValueError(f"An expired credit cannot be consumed")
        if self.get_remaining_value() >= value:
            movement = ConsumeCreditMovement(
                value, value, description or "Você consumiu créditos"
            )
            movement.set_movement_origin(object_type, object_id)
            self._usage_list.append(movement)
            return 0
        not_processed_value = value - self.get_remaining_value()
        remaining_value = self.get_remaining_value()
        movement = ConsumeCreditMovement(
            remaining_value, remaining_value, description or "Você consumiu créditos"
        )
        movement.set_movement_origin(object_type, object_id)
        self._usage_list.append(movement)
        return not_processed_value

    def renew(self) -> "CreditTransaction":
        add_movement = 0
        for movement in self._usage_list:
            if movement.operation_type.lower() not in ("add", "renew"):
                continue
            add_movement += movement.credit_movement
        transaction = CreditTransaction(
            creation_date=self.get_expiration_date(),
            account_id=self.account_id,
            type=self.type,
            contract_service_id=self.contract_service_id,
            contract_service_creation_date=self.contract_service_creation_date,
        )
        transaction.register_movement(
            RenewCreditMovement(
                add_movement,
                "Seus créditos foram renovados",
            )
        )
        return transaction

    def refund(self, object_type: str, object_id: str) -> None:
        for consume in self.get_consumed_movements():
            if consume.object_type != object_type or consume.object_id != object_id:
                continue
            if not self.can_refund(object_type, object_id):
                continue
            movement = RefundCreditMovement(
                consume.credit_movement,
                consume.operation_movement,
                "Seus créditos foram estornados",
                None,
                None,
            )
            movement.set_movement_origin(object_type, object_id)
            self.register_movement(movement)

    def expire(self, at: Optional[date] = None) -> None:
        if self.has_expired_operation() and self.is_expired(at or self.creation_date):
            return
        if not self.is_expired(at or self.creation_date):
            return
        movement = ExpireCreditMovement(
            self.get_remaining_value(),
            "Seus créditos expiraram",
            None,
            None,
        )
        self.register_movement(movement)

    def get_remaining_value(self, usage_list: List[SupportedMovements] = []) -> int:
        return sum(usage_list or self._usage_list)

    def is_expired(self, reference_date: Optional[date] = None) -> bool:
        reference_date = reference_date or self.creation_date
        return (
            reference_date >= self.get_expiration_date() or self.has_expired_operation()
        )

    def get_consumed_movements(self) -> List[ConsumeCreditMovement]:
        movements = []
        for use in self._usage_list:
            if use.operation_type.lower() != "consume":
                continue
            movements.append(use)
        return movements

    def get_consumed_value(self) -> int:
        consumed_value = 0
        for use in self.get_consumed_movements():
            consumed_value += use.credit_movement
        return consumed_value

    def has_expired_operation(self) -> bool:
        for transaction in self._usage_list:
            if transaction.operation_type.lower() == "expire":
                return True
        return False

    def get_expiration_date(self, at: Optional[date] = None) -> date:
        at = at or self.creation_date
        next_day = self.contract_service_creation_date.day
        next_year = at.year
        next_month = at.month + 1
        if next_month >= 13:
            next_month = 1
            next_year += 1
        next_month_max_day = monthrange(next_year, next_month)[-1]
        if next_day >= next_month_max_day:
            next_day = next_month_max_day
        return date(month=next_month, day=next_day, year=next_year)

    def get_expired_value(self, reference_date: date) -> int:
        # TODO: rename to not_consumed_as_expired
        if not self.is_expired(reference_date):
            return 0
        return sum(self._usage_list)

    def register_movement(self, movement: SupportedMovements) -> None:
        self._usage_list.append(movement)

    def can_refund(self, object_type: str, object_id: str) -> bool:
        for movement in self._usage_list:
            if (
                movement.operation_type.lower() == "refund"
                and movement.object_type == object_type
                and movement.object_id == object_id
            ):
                return False
        return True
