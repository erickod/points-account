import datetime
from datetime import date
from unittest import TestCase
from uuid import uuid1, uuid4

from credits_account.infra.repository.in_memory_credit_account_repository import (
    CreditAccountRow,
    CreditLogRow,
    CreditRow,
    InMemoryCreditAccountRepository,
    OperationLogRow,
)

company_id = uuid1()
credit_row_id = uuid1()
credit_log_row_id = uuid1()
operation_log_id = uuid1()
now = datetime.datetime(2022, 9, 1)
credit_account_rows = [
    CreditAccountRow(
        now,
        now,
        balance=10,
        company_id=company_id,
        id=company_id,
    )
]
credit_rows = [
    CreditRow(
        now,
        now,
        10,
        0,
        expiration_date=date(2022, 10, 1),
        type="subscription",
        account_id=company_id,
        id=credit_row_id,
    )
]
credit_log_rows = [
    CreditLogRow(
        now,
        now,
        10,
        account_id=company_id,
        credit_id=credit_row_id,
        operation_id=operation_log_id,
        id=credit_log_row_id,
    )
]
operation_log_row = [
    OperationLogRow(
        now,
        now,
        company_id,
        "Você adicionou créditos",
        10,
        "ADD",
        account_id=company_id,
        id=operation_log_id,
    )
]


class TestInMemoryCreditAccount(TestCase):
    def test_must_return_an_credit_account_with_previous_add_operation(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            credit_account_rows, credit_rows, credit_log_rows, operation_log_row
        )
        account = sut.load_account_by_company_id(company_id)
        assert account
        assert account.get_balance() == 10

    def test_ensure_can_handle_add_credits_from_credit_account(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            credit_account_rows, credit_rows, credit_log_rows, operation_log_row
        )
        account = sut.load_account_by_company_id(company_id)
        assert account
        assert account.get_balance() == 10
        account.add(100, "Você adicionou créditos", "subscription")
        assert account.get_balance() == 110
        sut.add_credits(account)
        recoveredAccount = sut.load_account_by_company_id(company_id)
        assert recoveredAccount.get_balance() == 110
        assert account != recoveredAccount
