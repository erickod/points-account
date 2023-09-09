from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from credits_account.application.cache_handler import CreditCacheHandler
from credits_account.application.consume_credit.protocols import CreditAccountRepository
from credits_account.domain.entities.credit_account import (
    ConsumeCreditOperation,
    MovementTarget,
)


@dataclass
class ConsumeCreditInput:
    company_id: UUID
    value: int
    description: str
    operation_owner_id: UUID
    target_id: Optional[UUID] = None
    target_type: str = ""


@dataclass
class ConsumeCreditOutput:
    account_id: UUID
    total_credits: int


class ConsumeCreditUC:
    def __init__(
        self,
        credit_account_repository: CreditAccountRepository,
        cache_handler=CreditCacheHandler,
    ) -> None:
        self._repo = credit_account_repository
        self._cache_handler = cache_handler

    def execute(self, input: ConsumeCreditInput) -> ConsumeCreditOutput:
        movement_target = MovementTarget(input.target_type, input.target_id)
        consume_operation = ConsumeCreditOperation(
            input.operation_owner_id, input.value, input.description
        )
        consume_operation.set_movement_target(movement_target)
        account = self._repo.load_account_by_company_id(input.company_id)
        account.consume(consume_operation)
        self._repo.consume_credits(account)
        self._cache_handler.clean_credits_cache_by_company_id(input.company_id)
        return ConsumeCreditOutput(account.id, account.balance)
