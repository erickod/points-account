from copy import deepcopy
from datetime import date
from queue import Queue
from typing import Any, List
from uuid import UUID

from credits_account.domain.entities import Credit
from credits_account.domain.entities.credit import CreditTransaction
from credits_account.domain.entities.operations.add_operation import AddCreditOperation
from credits_account.domain.entities.operations.consume_operation import (
    ConsumeCreditOperation,
)
from credits_account.domain.entities.operations.movement_target import MovementTarget
from credits_account.domain.entities.operations.operations import (
    ExpireCreditOperation,
    RefundCreditOperation,
)


class CreditAccount:
    def __init__(
        self,
        company_id: UUID,
        credit_state_list: List[CreditTransaction] = [],
        reference_date: date = date.today(),
    ) -> None:
        self._id = company_id
        self._fifo_queue = Queue()  # type:ignore
        self._credit_state_list: List[CreditTransaction] = credit_state_list
        self._reference_date: date = reference_date
        self._transactions: List[Any] = []
        self._consume_history: List[ConsumeCreditOperation] = []
        self.__put_initial_balance_on_fifo_queue()

    @staticmethod
    def restore(
        company_id: UUID,
        reference_date: date,
        credit_state_list: List[CreditTransaction] = [],
    ) -> "CreditAccount":
        account = CreditAccount(
            company_id,
            credit_state_list=credit_state_list,
            reference_date=reference_date,
        )
        return account

    def __put_initial_balance_on_fifo_queue(self) -> None:
        for credit in deepcopy(self._credit_state_list):
            self._fifo_queue.put(credit)

    def __ensure_account_has_enough_balance_to_consume(self, value: int) -> bool:
        if value > self.balance or value <= 0:
            raise ValueError(
                f"CreditAccount {self.get_id()} don't have enough balance to consume"
            )
        return True

    def add(self, operation: AddCreditOperation) -> None:
        credit = operation.make_credit(self._reference_date, self.get_id())
        if credit.account_id != self._id:
            raise ValueError("the credit account don't match the group account")
        self._fifo_queue.put(credit)
        self._transactions.append(operation)

    def consume(
        self,
        value: int,
        operation_owner_id: UUID,
        description: str = "",
        object_type: str = "",
        object_id: str = "",
    ) -> None:
        operation = ConsumeCreditOperation(value, operation_owner_id, description)
        self.__ensure_account_has_enough_balance_to_consume(operation.value)
        not_consumed_credit = operation.value
        while not self._fifo_queue.empty():
            credit = self._fifo_queue.get()
            not_consumed_credit = credit.consume(
                not_consumed_credit, reference_date=self._reference_date
            )
            operation.register_movement(credit)
            operation.set_movement_target(MovementTarget(object_type, object_id))
            if credit.remaining_value:
                break
        self._transactions.append(operation)

    def refund(self, operation: RefundCreditOperation) -> None:
        ...

    def expire(self, operation: ExpireCreditOperation) -> None:
        ...

    def renew(self) -> None:
        ...

    def get_id(self) -> UUID:
        return self._id

    def get_movements(self, type: str) -> List[Any]:
        return [
            movement
            for movement in self._transactions
            if movement.type.lower() == type.lower()
        ]

    @property
    def balance(self) -> int:
        total = 0
        for transaction in self._credit_state_list:
            total += transaction.get_remaining_value()
        return total

    @property
    def company_id(self) -> UUID:
        return self._id

    def __str__(self) -> str:
        string = f"CreditAccount(id={self.id}, "
        string += f"balance={self.balance}, consumed={self.consumed_value})"
        return string
