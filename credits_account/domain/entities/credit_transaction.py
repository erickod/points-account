import uuid
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from credits_account.domain.entities.credit_movement import CreditMovement
from credits_account.domain.entities.credit_movement.add_movement import (
    AddCreditMovement,
)
from credits_account.domain.entities.credit_movement.consume_moviment import (
    ConsumeCreditMovement,
)
from credits_account.domain.entities.credit_movement.renew_movement import (
    RenewCreditMovement,
)


@dataclass
class CreditTransaction:
    creation_date: date
    account_id: uuid.UUID
    type: str
    contract_service_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self) -> None:
        self._usage_list: List[CreditMovement] = []
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
            if movement.operation_type.lower() != "add":
                continue
            add_movement += movement.credit_movement
        transaction = CreditTransaction(
            creation_date=self.get_expiration_date(),
            account_id=self.account_id,
            type=self.type,
            contract_service_id=self.contract_service_id,
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
            movement = CreditMovement(
                consume.credit_movement,
                "REFUND",
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
        movement = CreditMovement(
            self.get_remaining_value(),
            "EXPIRE",
            self.get_remaining_value(),
            "Seus créditos expiraram",
            None,
            None,
        )
        self.register_movement(movement)

    def get_remaining_value(self, usage_list: [CreditMovement] = []) -> int:
        return sum(usage_list or self._usage_list)

    def is_expired(self, reference_date: Optional[date] = None) -> bool:
        reference_date = reference_date or self.creation_date
        return (
            reference_date >= self.get_expiration_date() or self.has_expired_operation()
        )

    def get_consumed_movements(self) -> List[CreditMovement]:
        movements = []
        for use in self._usage_list:
            if use.operation_type.lower() != "consume" or use.operation_id or use.id:
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

    def get_expiration_date(self, creation_date: Optional[date] = None) -> date:
        creation_date = creation_date or self.creation_date
        next_day = creation_date.day
        next_year = creation_date.year
        if next_day > 28:
            next_day = 28
        next_month = creation_date.month + 1
        if next_month >= 13:
            next_month = 1
            next_year += 1
        return date(month=next_month, day=next_day, year=next_year)

    def get_expired_value(self, reference_date: date) -> int:
        # TODO: rename to not_consumed_as_expired
        if not self.is_expired(reference_date):
            return 0
        return sum(self._usage_list)

    def register_movement(self, movement: CreditMovement) -> None:
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
