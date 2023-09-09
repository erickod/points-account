from typing import Any, Optional, Protocol
from uuid import UUID

from credits_account.domain.entities.credit_account import CreditAccount


class CreditAccountRepository(Protocol):
    def initialize_account(self, account: Any) -> None:
        pass

    def update(self, account: Any) -> None:
        pass

    def load_account_by_company_id(self, company_id: UUID) -> Optional[CreditAccount]:
        ...
