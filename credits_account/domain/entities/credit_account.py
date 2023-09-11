from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid1

from credits_account.domain.entities.credit_movement import CreditMovement
from credits_account.domain.entities.credit_transaction import CreditTransaction


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
            type=credit_type,
            contract_service_id=uuid1(),  # TODO: must receive a contracted_service as optional
            id=None,  # TODO: must be generated in the repository layer
        )
        assert (
            credit_state.account_id == self._id
        ), "the credit account don't match the group account"
        credit_state.add(value, description)
        self._credit_state_list.append(credit_state)
        self._transactions.append(credit_state)

    def consume(
        self,
        value: int,
        description: str,
        consumed_at: Optional[date] = None,
        object_type: str = "",
        object_id: str = "",
    ) -> None:
        if type(consumed_at) == datetime:
            consumed_at = consumed_at.date()
        self.__ensure_account_has_enough_balance_to_consume(value)
        total = int(value)
        for transaction in self._credit_state_list[::-1]:
            # TODO: create test to the below line
            if transaction.get_remaining_value() < 1 or transaction.is_expired(
                self._reference_date
            ):
                continue
            not_consumed_credit = transaction.consume(
                total,
                reference_date=consumed_at
                or date(
                    self._reference_date.year,
                    self._reference_date.month,
                    self._reference_date.day,
                ),
                object_type=object_type,
                object_id=object_id,
                description=description,
            )
            total = not_consumed_credit
            if not_consumed_credit < 0:
                break

    def expire(self, consumed_at: Optional[date] = None) -> None:
        if type(consumed_at) == datetime:
            consumed_at = consumed_at.date()
        for transaction in self._credit_state_list[::-1]:
            transaction.expire(self._reference_date)

    def refund(self, object_type: str, object_id: str) -> bool:
        for transaction in self._credit_state_list:
            transaction.refund(object_type, object_id)

    def renew(self) -> None:
        for credit in self._credit_state_list:
            if not credit.is_expired(self._reference_date):
                continue
            renewed_credit = credit.renew()
            if (
                renewed_credit in self._credit_state_list
                or renewed_credit in self._transactions
            ):
                continue
            self._transactions.append(renewed_credit)
            self._credit_state_list.append(renewed_credit)

    def get_id(self) -> UUID:
        return self._id

    def get_balance(self, at: Optional[date] = None) -> int:
        at = at or self._reference_date
        total = 0
        for transaction in self._credit_state_list:
            if transaction.is_expired(at):
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
        string += f"balance={self.get_balance()})"
        return string
