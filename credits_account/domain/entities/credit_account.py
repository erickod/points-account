from datetime import date
from typing import List
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
        self._transactions: List[CreditTransaction] = []

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
        if value > self.balance or value <= 0:
            raise ValueError(
                f"CreditAccount {self.get_id()} don't have enough balance to consume"
            )
        return True

    def add(self, value: int, description: str, credit_type: str) -> None:
        credit_state = CreditTransaction(
            reference_date=self._reference_date,
            account_id=self.get_id(),
            initial_value=0,
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
                uuid1(),
                value,
                description,
                uuid1(),
            )
        )
        self._credit_state_list.append(credit_state)
        self._transactions.append(credit_state)

    def consume(self, value: int, description: str) -> None:
        for transaction in self._credit_state_list[::-1]:
            not_consumed_credit = transaction.consume(value)
            movement = CreditMovement(
                value - not_consumed_credit,
                "CONSUME",
                uuid1(),
                value,
                description,
                uuid1(),
            )
            transaction.register_movement(
                movement
            )  # TODO: verify if it's needed because of reference system
            self._transactions.append(transaction)
            if not_consumed_credit:
                break

    def get_id(self) -> UUID:
        return self._id

    def get_balance(self) -> int:
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
