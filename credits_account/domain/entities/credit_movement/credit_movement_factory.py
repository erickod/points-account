import uuid
from dataclasses import dataclass
from typing import Any, Callable, Optional

from credits_account.domain.entities.credit_movement.add_movement import (
    AddCreditMovement,
)
from credits_account.domain.entities.credit_movement.consume_moviment import (
    ConsumeCreditMovement,
)
from credits_account.domain.entities.credit_movement.expire_movement import (
    ExpireCreditMovement,
)
from credits_account.domain.entities.credit_movement.refund_movement import (
    RefundCreditMovement,
)
from credits_account.domain.entities.credit_movement.renew_movement import (
    RenewCreditMovement,
)


@dataclass
class CreditMovementFactory:
    credit_movement: int
    operation_type: str
    operation_movement: int
    operation_log: str
    operation_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None

    def make(self) -> Any:
        callable: Callable = getattr(self, self.operation_type.lower())
        return callable()

    def add(self) -> AddCreditMovement:
        return AddCreditMovement(
            self.credit_movement,
            self.operation_log,
            self.operation_id,
            self.id,
        )

    def consume(self) -> ConsumeCreditMovement:
        return ConsumeCreditMovement(
            self.credit_movement,
            self.operation_movement,
            self.operation_log,
            self.operation_id,
            self.id,
        )

    def renew(self) -> RenewCreditMovement:
        return RenewCreditMovement(
            self.credit_movement,
            self.operation_log,
            self.operation_id,
            self.id,
        )

    def expire(self) -> RenewCreditMovement:
        return ExpireCreditMovement(
            self.credit_movement,
            self.operation_log,
            self.operation_id,
            self.id,
        )

    def refund(self) -> RefundCreditMovement:
        return RefundCreditMovement(
            self.credit_movement,
            self.operation_movement,
            self.operation_log,
            self.operation_id,
            self.id,
        )
