from datetime import date
from unittest import TestCase
from uuid import uuid1

from credits_account.domain.entities.credit import CreditTransaction


class TestCreditTransaction(TestCase):
    def test_given_a_creation_date_must_return_the_right_expiration_date(self) -> None:
        creation_date = date(2022, 10, 1)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            initial_value=10,
            type="subscription",
            account_id=account_id,
        )
        assert sut.get_expiration_date() == date(2022, 11, 1)

    def test_when_year_changes_ensure_it_get_the_right_expiration_date(self) -> None:
        creation_date = date(2022, 12, 28)
        account_id = uuid1()
        sut = CreditTransaction(
            creation_date=creation_date,
            initial_value=10,
            type="subscription",
            account_id=account_id,
        )
        assert sut.get_expiration_date() == date(2023, 1, 28)
