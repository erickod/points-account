import uuid
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CreditMovement:
    credit_movement: int
    operation_type: str
    operation_movement: int
    operation_log: str
    operation_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self) -> None:
        self.object_type: str = ""
        self.object_id: str = ""
        if (
            self.operation_type.lower() in ("consume", "expire")
            and self.credit_movement > 0
        ):
            self.credit_movement = self.credit_movement * -1
            self.operation_movement = self.operation_movement * -1

        if (
            self.operation_type.lower() in ("add", "refund")
            and self.credit_movement < 0
        ):
            self.credit_movement = self.credit_movement * -1
            self.operation_movement = self.operation_movement * -1

    def set_movement_origin(self, object_type, object_id) -> None:
        assert self.operation_type.lower() in ("consume", "refund")
        self.object_type = object_type
        self.object_id = object_id

    def __int__(self) -> int:
        return self.credit_movement

    def __add__(self, other: Any):
        return self.credit_movement + other

    def __radd__(self, other: Any):
        return other + self.credit_movement

    def __sub__(self, other: Any):
        return self.credit_movement - other
