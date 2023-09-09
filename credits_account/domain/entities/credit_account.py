from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid1

from credits_account.domain.entities.credit import CreditMovement, CreditTransaction


class CreditAccount:
    def __init__(
        self,
        company_id: UUID,
        credit_state_list: List[CreditTransaction],
        reference_date: date = date.today(),
    ) -> None:
        self._id = company_id
        self._credit_state_list: List[CreditTransaction] = credit_state_list
        self._reference_date: date = reference_date
        self._transactions: List[CreditTransaction] = [*credit_state_list]

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

    def __ensure_account_has_enough_balance_to_consume(self, value: int) -> bool:
        if value > self.get_balance() or value <= 0:
            raise ValueError(
                f"CreditAccount {self.get_id()} don't have enough balance to consume"
            )
        return True

    def add(self, value: int, description: str, credit_type: str) -> None:
        credit_state = CreditTransaction(
            creation_date=self._reference_date,
            account_id=self.get_id(),
            initial_value=0,  # TODO: remove this param
            type=credit_type,
            contract_service_id=uuid1(),  # TODO: must receive a contracted_service as optional
            id=None,  # TODO: must be generated in the repository layer
        )
        assert (
            credit_state.account_id == self._id
        ), "the credit account don't match the group account"
        credit_state.register_movement(
            CreditMovement(
                value,
                "ADD",
                value,
                description,
                None,
                None,
            )
        )
        self._credit_state_list.append(credit_state)
        self._transactions.append(credit_state)

    def consume(
        self, value: int, description: str, consumed_at: Optional[date] = None
    ) -> None:
        if type(consumed_at) == datetime:
            consumed_at = consumed_at.date()
        self.__ensure_account_has_enough_balance_to_consume(value)
        total = int(value)
        for i, transaction in enumerate(self._credit_state_list[::-1]):
            not_consumed_credit = transaction.consume(
                total,
                reference_date=consumed_at
                or date(
                    self._reference_date.year,
                    self._reference_date.month,
                    self._reference_date.day,
                ),
            )
            to_be_consumed = total - not_consumed_credit
            movement = CreditMovement(
                to_be_consumed,
                "CONSUME",
                value,
                description,
                None,
                None,
            )
            total = not_consumed_credit
            if not_consumed_credit < 0:
                break
            transaction.register_movement(movement)

    def expire(self, consumed_at: Optional[date] = None) -> None:
        if type(consumed_at) == datetime:
            consumed_at = consumed_at.date()
        for transaction in self._credit_state_list[::-1]:
            if transaction.has_expired_operation():
                continue
            movement = CreditMovement(
                transaction.get_remaining_value(),
                "EXPIRE",
                transaction.get_remaining_value(),
                "Seus créditos expiraram",
                None,
                None,
            )
            transaction.register_movement(movement)

    def get_id(self) -> UUID:
        return self._id

    def get_balance(self) -> int:
        total = 0
        for transaction in self._credit_state_list:
            if transaction.is_expired(self._reference_date):
                continue
            total += transaction.get_remaining_value()
        return total

    def count_expired(self) -> int:
        total = 0
        for transaction in self._credit_state_list:
            if not transaction.is_expired(self._reference_date):
                continue
            total += transaction.get_remaining_value()
        return total

    @property
    def company_id(self) -> UUID:
        return self._id

    def __str__(self) -> str:
        string = f"CreditAccount(id={self.get_id()}, "
        string += f"balance={self.get_balance()}, consumed={0})"
        return string
