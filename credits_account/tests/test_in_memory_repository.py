import datetime
from copy import deepcopy
from datetime import date
from typing import Any, List
from unittest import TestCase
from uuid import uuid1

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
now = datetime.date(2022, 9, 1)


def get_account_rows() -> List[CreditAccountRow]:
    return deepcopy(
        [
            CreditAccountRow(
                now,
                now,
                balance=10,
                company_id=company_id,
                id=company_id,
            )
        ]
    )


def get_credit_rows() -> List[CreditRow]:
    return deepcopy(
        [
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
    )


def get_credit_log_rows() -> List[Any]:
    return deepcopy(
        [
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
    )


def get_operation_log_row() -> List[Any]:
    return deepcopy(
        [
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
    )


class TestInMemoryCreditAccount(TestCase):
    def test_must_return_an_credit_account_with_previous_add_operation(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            get_account_rows(),
            get_credit_rows(),
            get_credit_log_rows(),
            get_operation_log_row(),
        )
        sut.contracted_service_creation_date = now
        account = sut.load_account_by_company_id(company_id)
        account._reference_date = now
        assert account
        assert account.get_balance() == 10
        recovered_credit = account._credit_state_list[0]
        assert recovered_credit.contract_service_creation_date == now

    def test_ensure_can_handle_add_credits_from_credit_account(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            get_account_rows(),
            get_credit_rows(),
            get_credit_log_rows(),
            get_operation_log_row(),
        )
        account = sut.load_account_by_company_id(company_id)
        account._reference_date = now
        assert account
        assert account.get_balance() == 10
        account.add(100, "Você adicionou créditos", "subscription")
        assert account.get_balance() == 110
        sut.add_credits(account)
        recoveredAccount = sut.load_account_by_company_id(company_id)
        recoveredAccount._reference_date = now
        assert recoveredAccount.get_balance() == 110
        assert account != recoveredAccount

    def test_ensure_can_handle_consume_credits_from_credit_account(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            get_account_rows(),
            get_credit_rows(),
            get_credit_log_rows(),
            get_operation_log_row(),
        )
        account = sut.load_account_by_company_id(company_id)
        account._reference_date = now
        assert account
        assert account.get_balance() == 10
        account.consume(5, "Você consumiu créditos", consumed_at=now)
        assert account.get_balance() == 5
        account.consume(3, "Você consumiu créditos", consumed_at=now)
        assert account.get_balance() == 2
        sut.consume_credits(account)
        recoveredAccount = sut.load_account_by_company_id(company_id)
        recoveredAccount._reference_date = now
        assert recoveredAccount.get_balance() == 2
        assert account != recoveredAccount

    def test_expire(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            get_account_rows(),
            get_credit_rows(),
            get_credit_log_rows(),
            get_operation_log_row(),
        )
        account = sut.load_account_by_company_id(company_id)
        account._reference_date = now
        assert account
        assert account.get_balance() == 10
        account._reference_date = date(2022, 10, 1)
        account.expire()
        sut.expire(account)
        recoveredAccount = sut.load_account_by_company_id(company_id)
        recoveredAccount._reference_date = date(2022, 10, 1)
        assert account.get_balance() == 0
        assert (
            recoveredAccount._transactions[-1]._usage_list[-1].operation_type
            == "EXPIRE"
        )

    def test_ensure_expire_cannot_log_two_expire_operations(self) -> None:
        sut = InMemoryCreditAccountRepository.populate(
            get_account_rows(),
            get_credit_rows(),
            get_credit_log_rows(),
            get_operation_log_row(),
        )
        account = sut.load_account_by_company_id(company_id)
        account._reference_date = now
        assert account
        assert account.get_balance() == 10
        account._reference_date = date(2022, 10, 1)
        account.expire()
        account.expire()
        sut.expire(account)
        recoveredAccount = sut.load_account_by_company_id(company_id)
        account._reference_date = date(2022, 10, 1)
        assert account.get_balance() == 0
        assert (
            recoveredAccount._transactions[-1]._usage_list[-1].operation_type
            == "EXPIRE"
        )
        assert (
            recoveredAccount._transactions[-1]._usage_list[-2].operation_type
            != "EXPIRE"
        )
