from dataclasses import dataclass
from datetime import date
from typing import Any, Optional
from uuid import UUID

from credits_account.application.add_credit.protocols import CreditAccountRepository
from credits_account.application.cache_handler import CreditCacheHandler
from credits_account.domain.entities.credit import Credit as CreditEntity
from credits_account.domain.entities.credit_account import (
    AddCreditOperation,
    CreditAccount,
)


@dataclass
class AddCreditInput:
    company_id: UUID
    value: int
    operation_owner_id: UUID
    credit_type: str = "SUBSCRIPTION"
    description: str = "Você adicionou créditos"
    target_id: Optional[UUID] = None
    target_type: str = ""
    contracted_service_id: Optional[UUID] = None


@dataclass
class AddCreditOutput:
    account_id: UUID
    total_credits: int


class AddCreditUC:
    def __init__(
        self,
        credit_account_repository: CreditAccountRepository,
        cache_handler=CreditCacheHandler,
    ) -> None:
        self._repo = credit_account_repository
        self._cache_handler = cache_handler

    def execute(self, input: AddCreditInput) -> Any:
        account = self._repo.load_account_by_company_id(input.company_id)
        if account == None:
            account = CreditAccount(company_id=input.company_id)
            self._repo.create_account(account)
        add_operation = AddCreditOperation(
            input.value,
            input.operation_owner_id,
            input.description,
        )
        assert account != None
        account.add(add_operation)
        self._repo.add_credits(account)
        self._cache_handler.clean_credits_cache_by_company_id(input.company_id)
        return AddCreditOutput(account.get_id(), account.balance)
