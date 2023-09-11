import uuid
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AddCreditMovement:
    credit_movement: int
    operation_log: str
    operation_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self) -> None:
        self.operation_type: str = "ADD"
        self.operation_movement = self.credit_movement
        if self.credit_movement < 0:
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
