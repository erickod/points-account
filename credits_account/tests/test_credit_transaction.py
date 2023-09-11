from datetime import date
from unittest import TestCase
from uuid import uuid1

from credits_account.domain.entities import CreditTransaction
from credits_account.domain.entities.credit_movement import CreditMovement


class TestCreditTransaction(TestCase):
    def test_given_a_creation_date_must_return_the_right_expiration_date(self) -> None:
        creation_date = date(2022, 10, 1)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            type="subscription",
            account_id=account_id,
        )
        assert sut.get_expiration_date() == date(2022, 11, 1)

    def test_when_year_changes_ensure_it_get_the_right_expiration_date(self) -> None:
        creation_date = date(2022, 12, 28)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            type="subscription",
            account_id=account_id,
        )
        assert sut.get_expiration_date() == date(2023, 1, 28)

    def test_given_a_creation_date_a_transaction_must_be_expired_one_month_after(
        self,
    ) -> None:
        creation_date = date(2022, 12, 28)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            type="subscription",
            account_id=account_id,
        )
        assert sut.is_expired(date(2023, 1, 28))

    def test_when_a_credit_is_valid_and_has_value_to_be_consumed_consume_must_log_the_operation_and_change_remaining_value(
        self,
    ) -> None:
        creation_date = date(2022, 12, 28)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            type="subscription",
            account_id=account_id,
        )
        sut.register_movement(CreditMovement(10, "ADD", 10, "Você adicionou créditos"))
        assert sut.get_remaining_value() == 10
        sut.consume(10, reference_date=creation_date)
        assert sut.get_remaining_value() == 0
        # assert len(sut.get_consumed_movements()) == 1
