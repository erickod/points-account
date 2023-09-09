import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any, List, Optional, Tuple


@dataclass
class CreditLog:
    total_movimented: int
    movement_type: str
    description: str
    object_type: str = ""
    object_id: str = ""
    id: Optional[uuid.UUID] = None

    def __int__(self) -> int:
        return self.total_movimented


@dataclass
class CreditMovement:
    credit_movement: int
    operation_type: str
    operation_movement: int
    operation_log: str
    operation_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self) -> None:
        if (
            self.operation_type.lower() in ("consume", "expire")
            and self.credit_movement > 0
        ):
            self.credit_movement = self.credit_movement * -1
            self.operation_movement = self.operation_movement * -1

    def __int__(self) -> int:
        return self.credit_movement

    def __add__(self, other: Any):
        return self.credit_movement + other

    def __radd__(self, other: Any):
        return other + self.credit_movement

    def __sub__(self, other: Any):
        return self.credit_movement - other


@dataclass
class CreditTransaction:
    creation_date: date
    account_id: uuid.UUID
    initial_value: int
    type: str
    contract_service_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self) -> None:
        self._usage_list: List[CreditMovement] = []
        if not self.creation_date:
            self.creation_date = date.today()

    def __key(self) -> Tuple[str, str]:
        return ("" if not self.id else self.id.hex, str(self.creation_date))

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CreditTransaction):
            return self.__key() == other.__key()
        return False

    def consume(
        self,
        value: int,
        *,
        ignore_is_expired_check: bool = False,
        reference_date=date.today(),
    ) -> int:
        assert value >= 0, "The consume credit value should be greater than 0"
        if self.is_expired(reference_date) and not ignore_is_expired_check:
            raise ValueError(f"An expired credit cannot be consumed")
        local_usage_list = deepcopy(self._usage_list)
        if self.get_remaining_value(usage_list=local_usage_list) >= value:
            local_usage_list.append(value)
            return 0
        not_processed_value = value - self.get_remaining_value(
            usage_list=local_usage_list
        )
        remaining_value = self.get_remaining_value(usage_list=local_usage_list)
        local_usage_list.append(remaining_value)
        return not_processed_value

    def get_remaining_value(self, usage_list: [CreditMovement] = []) -> int:
        return sum(usage_list or self._usage_list)
        return self.initial_value + sum(usage_list or self._usage_list)

    def is_expired(self, reference_date: date) -> bool:
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
        return self.initial_value - sum(self._usage_list)

    def register_movement(self, movement: CreditMovement) -> None:
        self._usage_list.append(movement)
