from calendar import monthrange
from datetime import date, timedelta
from unittest import TestCase
from uuid import uuid1

from credits_account.domain.entities.credit_transaction import CreditTransaction

order_date = date(2022, 1, 28)


class TestCreditTransactionFixedExpirationDates(TestCase):
    def test_get_expiration_date_when_current_month_is_January(
        self,
    ) -> None:
        current_date = date(2022, 1, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 2, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_February(
        self,
    ) -> None:
        current_date = date(2022, 2, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 3, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_March(
        self,
    ) -> None:
        current_date = date(2022, 3, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 4, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_April(
        self,
    ) -> None:
        current_date = date(2022, 4, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 5, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_May(
        self,
    ) -> None:
        current_date = date(2022, 5, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 6, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_June(
        self,
    ) -> None:
        current_date = date(2022, 6, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 7, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_July(
        self,
    ) -> None:
        current_date = date(2022, 7, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 8, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_August(
        self,
    ) -> None:
        current_date = date(2022, 8, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 9, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_September(
        self,
    ) -> None:
        current_date = date(2022, 9, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 10, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_October(
        self,
    ) -> None:
        current_date = date(2022, 10, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 11, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_November(
        self,
    ) -> None:
        current_date = date(2022, 11, 28)
        account_id = uuid1()
        expected_expiration_date = date(2022, 12, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date

    def test_get_expiration_date_when_current_month_is_December(
        self,
    ) -> None:
        current_date = date(2022, 12, 28)
        account_id = uuid1()
        expected_expiration_date = date(2023, 1, 28)
        sut = CreditTransaction(
            creation_date=current_date,
            type="subscription",
            account_id=account_id,
        )
        sut.contract_service_creation_date = order_date
        assert not sut.is_expired(expected_expiration_date - timedelta(days=1))
        assert sut.is_expired(expected_expiration_date)
        assert sut.get_expiration_date() == expected_expiration_date
