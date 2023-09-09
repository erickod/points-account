from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid1

from credits_account.domain.entities.credit import CreditMovement, CreditTransaction
from credits_account.domain.entities.credit_account import CreditAccount


@dataclass
class CreditAccountRow:
    created_at: datetime
    updated_at: datetime
    id: UUID
    balance: int
    company_id: UUID


@dataclass
class CreditRow:
    created_at: datetime
    updated_at: datetime
    initial_value: int
    consumed_value: int
    expiration_date: date
    type: str
    account_id: UUID
    id: UUID
    contracted_service_id: Optional[UUID] = None


@dataclass
class CreditLogRow:
    created_at: datetime
    updated_at: datetime
    credit_moviment: int
    account_id: UUID
    credit_id: UUID
    operation_id: UUID
    id: UUID


@dataclass
class OperationLogRow:
    created_at: datetime
    updated_at: datetime
    owner_id: UUID
    description: str
    total_movement: int
    operation: str
    account_id: UUID
    id: UUID
    object_type: str = ""
    object_id: str = ""


class InMemoryCreditAccountRepository:
    def __init__(self) -> None:
        self.credit_account_rows: Dict[UUID, CreditAccountRow] = {}
        self.credit_rows: Dict[UUID, CreditRow] = {}
        self.credit_logs_rows: Dict[UUID, CreditLogRow] = {}
        self.operation_logs_rows: Dict[UUID, OperationLogRow] = {}

    @staticmethod
    def populate(
        credit_account_rows: List[CreditAccountRow],
        credit_rows: List[CreditRow],
        credit_logs_rows: List[CreditLogRow],
        operation_logs_rows: List[OperationLogRow],
    ) -> "InMemoryCreditAccountRepository":
        repo = InMemoryCreditAccountRepository()
        InMemoryCreditAccountRepository._add_to_field(
            repo.credit_account_rows, credit_account_rows, "id"
        )
        InMemoryCreditAccountRepository._add_to_field(
            repo.credit_rows, credit_rows, "account_id"
        )
        InMemoryCreditAccountRepository._add_to_field(
            repo.credit_logs_rows, credit_logs_rows, "account_id"
        )
        InMemoryCreditAccountRepository._add_to_field(
            repo.operation_logs_rows, operation_logs_rows, "account_id"
        )
        return repo

    @staticmethod
    def _add_to_field(
        target_container: Dict[UUID, Any],
        list_container: List[Any],
        id_field: str,
    ) -> None:
        for item in list_container:
            target_container[getattr(item, id_field)] = item

    def create_account(self, account: CreditAccount) -> None:
        now = datetime.now()
        row = CreditAccountRow(
            created_at=now,
            updated_at=now,
            id=account.get_id(),
            balance=account.balance,
            company_id=account.company_id,
        )
        self.credit_account_rows[account.company_id] = row

    def load_account_by_company_id(self, company_id: UUID) -> Optional[CreditAccount]:
        now = datetime.now()
        credit_account_row = self.credit_account_rows.get(company_id)
        if not credit_account_row:
            return None
        credits_movements: List[CreditTransaction] = []
        for credit in self.credit_rows.values():
            credit_state = CreditTransaction(
                creation_date=credit.created_at,
                account_id=credit_account_row.id,
                type=credit.type,
                contract_service_id=credit.contracted_service_id,
                id=credit.id,
            )
            if credit_state not in credits_movements:
                credits_movements.append(credit_state)
            for clog in self.credit_logs_rows.values():
                if clog.credit_id != credit.id:
                    continue
                for olog in self.operation_logs_rows.values():
                    if olog.id != clog.operation_id:
                        continue
                    movement = CreditMovement(
                        clog.credit_moviment,
                        olog.operation,
                        clog.operation_id,
                        olog.total_movement,
                        olog.description,
                        clog.id,
                    )
                    credit_state.register_movement(movement)

        credit_account = CreditAccount.restore(
            company_id=credit_account_row.company_id,
            reference_date=date.today(),
            credit_state_list=credits_movements,
        )
        return credit_account

    def add_credits(self, account: CreditAccount) -> None:
        now = account._reference_date
        for credit in account._transactions:
            if credit.id:
                continue
            credit.id = uuid1()
            credit_row = CreditRow(
                created_at=now,
                updated_at=now,
                initial_value=credit.get_remaining_value(),
                consumed_value=credit.get_consumed_value(),
                expiration_date=credit.get_expiration_date(),
                type=credit.type,
                account_id=account.get_id(),
                id=credit.id,
                contracted_service_id=credit.contract_service_id,
            )
            self.credit_rows[credit.id] = credit_row
            for use in credit._usage_list:
                if not use.id:
                    use.id = uuid1()
                if not use.operation_id:
                    use.operation_id = uuid1()
                credit_log = CreditLogRow(
                    created_at=now,
                    updated_at=now,
                    credit_moviment=use.credit_movement,
                    account_id=account.get_id(),
                    credit_id=credit.id,
                    operation_id=use.operation_id,
                    id=use.id,
                )
                self.credit_logs_rows[credit_log.id] = credit_log
                operation_log = OperationLogRow(
                    created_at=now,
                    updated_at=now,
                    owner_id=uuid1(),  # TODO: find a way to get it from input
                    description=use.operation_log,
                    total_movement=use.operation_movement,
                    operation=use.operation_type,
                    account_id=account.get_id(),
                    id=use.operation_id,
                    object_type="",
                    object_id="",
                )
                self.operation_logs_rows[operation_log.id] = operation_log

    def consume_credits(self, account: CreditAccount) -> None:
        now = account._reference_date
        for credit in account._transactions:
            if not credit.id or not credit.get_consumed_value():
                continue
            for use in credit.get_consumed_movements():
                if not use.id:
                    use.id = uuid1()
                if not use.operation_id:
                    use.operation_id = uuid1()
                credit_log = CreditLogRow(
                    created_at=now,
                    updated_at=now,
                    credit_moviment=use.credit_movement,
                    account_id=account.get_id(),
                    credit_id=credit.id,
                    operation_id=use.operation_id,
                    id=use.id,
                )
                self.credit_logs_rows[credit_log.id] = credit_log
                operation_log = OperationLogRow(
                    created_at=now,
                    updated_at=now,
                    owner_id=uuid1(),  # TODO: find a way to get it from input
                    description=use.operation_log,
                    total_movement=use.operation_movement,
                    operation=use.operation_type,
                    account_id=account.get_id(),
                    id=use.operation_id,
                    object_type=use.object_type,
                    object_id=use.object_id,
                )
                self.operation_logs_rows[operation_log.id] = operation_log

    def expire(self, account: CreditAccount) -> None:
        now = account._reference_date
        for credit in account._transactions:
            if not credit.id or not credit.is_expired(now):
                continue
            for use in credit._usage_list:
                if use.operation_type != "EXPIRE":
                    continue
                if not use.id:
                    use.id = uuid1()
                if not use.operation_id:
                    use.operation_id = uuid1()
                credit_log = CreditLogRow(
                    created_at=now,
                    updated_at=now,
                    credit_moviment=use.credit_movement,
                    account_id=account.get_id(),
                    credit_id=credit.id,
                    operation_id=use.operation_id,
                    id=use.id,
                )
                self.credit_logs_rows[credit_log.id] = credit_log
                operation_log = OperationLogRow(
                    created_at=now,
                    updated_at=now,
                    owner_id=uuid1(),  # TODO: find a way to get it from input
                    description=use.operation_log,
                    total_movement=use.operation_movement,
                    operation=use.operation_type,
                    account_id=account.get_id(),
                    id=use.operation_id,
                    object_type="",
                    object_id="",
                )
                self.operation_logs_rows[operation_log.id] = operation_log
