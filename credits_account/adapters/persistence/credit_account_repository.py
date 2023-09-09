from datetime import date, datetime, timedelta
from typing import Iterable, Optional, Dict
from uuid import UUID
from django.db.models import Q
from credits_account.domain import (
    CreditEntity,
    AccountEntity, 
    CreditAccount,
    CreditAccountHistory
)
from credits_account.models import Account, Credit, OperationLog, CreditsLog
from credits_account.domain.credit_account import AddCreditOperation, ConsumeCreditOperation, ExpireCreditOperation, MovementTarget, RefundCreditOperation
from credits_account.domain.credit import Contract
from users.models import User
from company.models import Company
from contracted_services.models import ContractedService
from pub_sub import dispatch_events_output
from django.db import transaction


class DjangoCreditAccountRepository:
    def __init__(self) -> None:
        self._account_manager = Account.objects
        self._credit_manager = Credit.objects
        self._credit_log_manager = CreditsLog.objects
        self._operation_log_manager = OperationLog.objects
        self._cs_manager = ContractedService.objects
        self._user_manager = User.objects
        self._company_manager = Company.objects

    def load_account_by_company_id(self, company_id: Optional[UUID]) -> Optional[CreditAccount]:
        account_orm:Account = self._account_manager.filter(company_id=company_id).first()
        if not account_orm: return
        today = date.today()
        credits_orm = self._credit_manager.filter(account=account_orm, expiration_date__gte=today)
        initial_balance_credits = []
        for credit in credits_orm:
            credit_entity = CreditEntity(
                credit.expiration_date,
                credit.account.id,
                credit.current_value,
                credit.type,
                credit.contracted_service_id,
                credit.id
            )
            initial_balance_credits.append(credit_entity)
        credit_account = CreditAccount(
            company_id,
            initial_balance_credits,
            self._load_history(account_orm.id),
            today,
            account_orm.id
        )
        return credit_account

    def create_account(self, credit_account: CreditAccount) -> None:
        company = self._company_manager.get(id=credit_account.company_id)
        credit_account_orm = Account(
            company=company,
            balance=0
        )
        credit_account_orm.save()
        credit_account._id = credit_account_orm.id
    
    @transaction.atomic
    def add_credits(self, account:CreditAccount) -> None:
        account_orm:Account = self._account_manager.get(id=account.id)
        for movement in account.get_movements("ADD"):
            for credit in movement.credits:
                operation_log_orm = OperationLog(
                    sponsor=self._user_manager.get(id=movement.operation_owner_id),
                    description=movement.description,
                    account=account_orm,
                    credit_movement=credit.value,
                    operation=movement.type
                )
                credit_orm = Credit(
                    value=credit.value,
                    account=account_orm,
                    expiration_date=credit.expiration_date,
                    current_value=credit.remaining_value,
                    type=credit.type,
                    contracted_service=self._cs_manager.filter(id=credit.contract_service_id).first()
                )
                credit_orm.save()
                operation_log_orm.save()
                credit_log = CreditsLog(
                    credit=credit_orm, 
                    operation_log=operation_log_orm, 
                    value=credit_orm.value
                )
                credit_log.save()
        account_orm.balance = account.balance
        account_orm.save()

    @transaction.atomic
    def consume_credits(self, account:CreditAccount) -> None:
        account_orm:Account = self._account_manager.get(id=account.id)
        for movement in account.get_movements("CONSUME"):
            operation_log_orm = OperationLog(
                sponsor=self._user_manager.get(id=movement.operation_owner_id),
                description=movement.description,
                account=account_orm,
                credit_movement=-abs(account_orm.balance - account.balance),
                operation=movement.type,
                object_type=movement.target.object_type,
                object_id=movement.target.object_id,
            )
            operation_log_orm.save()
            for credit in movement.credits:
                credit_orm = self._credit_manager.get(id=credit.id)
                credit_orm.current_value = credit.remaining_value
                credit_orm.save()
                credit_log_orm = CreditsLog(
                    credit=credit_orm, 
                    operation_log=operation_log_orm,
                    value=credit.consumed_value
                )
                credit_log_orm.save()
        account_orm.balance = account.balance
        account_orm.save()

    def _load_history(self, account_id:str) -> CreditAccountHistory:
        account_history = CreditAccountHistory()
        operations = self._operation_log_manager.filter(account_id=account_id, created_at__gte=date.today() - timedelta(days=90))
        for operation in operations:
            credits_log = self._credit_log_manager.filter(operation_log_id=operation.id)
            credits_list = []
            for credit_log in credits_log:
                credit_orm = self._credit_manager.get(id=credit_log.credit_id)
                contract_orm:ContractedService = ContractedService.objects.filter(id=credit_orm.contracted_service_id).first()
                credit_entity = CreditEntity(
                    credit_orm.expiration_date,
                    account_id,
                    credit_log.value,
                    credit_orm.type,
                    credit_orm.contracted_service_id,
                    id=credit_log.credit_id
                )
                if contract_orm:
                    credit_entity.configure_contract(Contract(
                        contract_orm.id,
                        contract_orm.status_financeiro == "ativo"
                    ))
                credits_list.append(credit_entity)

            if operation.operation == "ADD":
                credit_operation = AddCreditOperation(
                    operation.sponsor_id,
                )
            if operation.operation == "CONSUME":
                credit_operation = ConsumeCreditOperation(
                    operation.sponsor_id,
                    operation.credit_movement,
                    operation.description,
                    id=operation.id
                )
                credit_operation.set_movement_target(MovementTarget(
                    operation.object_type,
                    operation.object_id,
                ))
            if operation.operation == "REFUND":
                credit_operation = RefundCreditOperation(
                    operation.sponsor_id,
                    operation.account.id,
                    operation.object_type,
                    operation.object_id,
                )
            if operation.operation == "EXPIRE":
                credit_operation = ExpireCreditOperation(
                    operation.sponsor_id,
                )
            credit_operation.credits = credits_list
            account_history.register_operation(credit_operation) 
        return account_history

    @transaction.atomic
    def refund_credits(self, account:CreditAccount) -> None:
        account_orm = self._account_manager.get(id=account.id)
        operations = account.get_movements("REFUND")
        for operation in operations:
            refund_operation = OperationLog(
                sponsor=self._user_manager.get(id=operation.operation_owner_id),
                description=operation.description,
                account=account_orm,
                credit_movement=sum([credit.value for credit in operation.credits]),
                operation="REFUND",
                object_type=operation.target.object_type,
                object_id=operation.target.object_id,
            )
            refund_operation.save()
            for credit in operation.credits:
                refunded_credit = Credit(
                    value = credit.value,
                    account = account_orm,
                    expiration_date = credit.expiration_date,
                    current_value = credit.value,
                    type = credit.type,
                    contracted_service=self._cs_manager.filter(id=credit.contract_service_id).first()
                )
                refunded_credit.save()
                credit_log = CreditsLog(
                    credit=refunded_credit, 
                    operation_log=refund_operation, 
                    value=refunded_credit.current_value
                )
                credit_log.save()
        account_orm.balance = account.balance
        account_orm.save()

    @transaction.atomic
    def expire(self, account:Account) -> None:
        account_orm = self._account_manager.get(id=account.id)
        operations = account.get_movements("EXPIRE")
        for operation in operations:
            for credit in operation.credits:
                credit_orm = Credit.objects.get(id=credit.id)
                if not credit_orm.current_value: continue
                expire_operation = OperationLog(
                    sponsor=self._user_manager.get(id=operation.operation_owner_id),
                    description=operation.description,
                    account=account_orm,
                    credit_movement=-abs(credit_orm.current_value),
                    operation="EXPIRE",
                    object_type=None,
                    object_id=None,
                )
                expire_operation.save()
                credit_log = CreditsLog(
                    credit=credit_orm, 
                    operation_log=expire_operation, 
                    value=credit_orm.current_value
                )
                credit_log.save()
        account_orm.balance = account.balance
        account_orm.save()