import uuid
from datetime import date
from unittest import TestCase

from credits_account.domain.entities.credit import CreditMovement, CreditTransaction
from credits_account.domain.entities.credit_account import CreditAccount

company_id = uuid.uuid1()


class TestCreditAccount(TestCase):
    def test_ensure_is_created_with_balance_equals_zero(self) -> None:
        sut = CreditAccount(company_id=company_id, credit_state_list=[])
        self.assertEqual(sut.get_balance(), 0)

    def test_ensure_it_raises_when_try_to_consume_when_has_no_available_balance(
        self,
    ) -> None:
        sut = CreditAccount(company_id=company_id, credit_state_list=[])
        self.assertEqual(sut.get_balance(), 0)
        with self.assertRaises(ValueError):
            sut.consume(1, "Você adicionou créditos")
        self.assertEqual(sut.get_balance(), 0)

    def test_ensure_add_credits_updates_balance(self) -> None:
        sut = CreditAccount(company_id=company_id, credit_state_list=[])
        self.assertEqual(sut.get_balance(), 0)
        sut.add(10, "Você adicionou créditos", "subscription")
        self.assertEqual(sut.get_balance(), 10)

    def test_ensure_consume_credits_updates_balance(self) -> None:
        sut = CreditAccount(company_id=company_id, credit_state_list=[])
        self.assertEqual(sut.get_balance(), 0)
        sut.add(100, "Você adicionou créditos", "subscription")
        self.assertEqual(sut.get_balance(), 100)
        sut.consume(5, "Você consumiu créditos")
        self.assertEqual(sut.get_balance(), 95)
        sut.consume(5, "Você consumiu créditos")
        self.assertEqual(sut.get_balance(), 90)

    def test_ensure_balance_dont_count_expired_credits(self) -> None:
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(10, "Você adicionou créditos", "subscription")
        self.assertEqual(sut.get_balance(), 10)
        sut._reference_date = date(2022, 11, 1)
        self.assertEqual(sut.get_balance(), 0)

    def test_ensure_not_consumed_expired_credits_are_counted_as_expired(self) -> None:
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(10, "Você adicionou créditos", "subscription")
        self.assertEqual(sut.get_balance(), 10)
        sut.add(10, "Você adicionou créditos", "subscription")
        self.assertEqual(sut.get_balance(), 20)
        sut._reference_date = date(2022, 11, 1)
        self.assertEqual(sut.get_balance(), 0)
        self.assertEqual(sut.count_expired(), 20)

    def test_ensure_expire_log_expire_movement(self) -> None:
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(10, "Você adicionou créditos", "subscription")
        sut._reference_date = date(2022, 11, 1)
        self.assertEqual(sut.count_expired(), 10)
        sut.expire()
        self.assertEqual(
            sut._credit_state_list[-1]._usage_list[-1].operation_type, "EXPIRE"
        )

    def test_add_and_consume_together(self) -> None:
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(5, "Você adicionou créditos", "subscription")
        sut.add(5, "Você adicionou créditos", "subscription")
        sut.consume(6, "Você consumiu créditos")
        assert sut.get_balance() == 4

    def test_refund(self) -> None:
        object_type = "booking"
        object_id = "51dc3bbc-216b-4531-b15f-a8912973b600"
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(5, "Você adicionou créditos", "subscription")
        sut.add(5, "Você adicionou créditos", "subscription")
        assert sut.get_balance() == 10
        sut.consume(
            6,
            "Você consumiu créditos",
            object_type=object_type,
            object_id=object_id,
        )
        assert sut.get_balance() == 4
        sut.refund(object_type=object_type, object_id=object_id)
        assert sut.get_balance() == 10

    def test_refund_cannot_refund_the_same_object_twice_or_more(self) -> None:
        object_type = "booking"
        object_id = "51dc3bbc-216b-4531-b15f-a8912973b600"
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[],
            reference_date=date(2022, 10, 1),
        )
        self.assertEqual(sut.get_balance(), 0)
        sut.add(5, "Você adicionou créditos", "subscription")
        sut.add(5, "Você adicionou créditos", "subscription")
        assert sut.get_balance() == 10
        sut.consume(
            6,
            "Você consumiu créditos",
            object_type=object_type,
            object_id=object_id,
        )
        assert sut.get_balance() == 4
        sut.refund(object_type=object_type, object_id=object_id)
        assert sut.get_balance() == 10
        sut.refund(object_type=object_type, object_id=object_id)
        assert sut.get_balance() == 10

    def test_renew(self) -> None:
        reference_date = date(2022, 10, 1)
        expired_credit = CreditTransaction(
            creation_date=reference_date,
            account_id=company_id,
            type="subscription",
            contract_service_id=uuid.uuid1(),
        )
        expired_credit.register_movement(
            CreditMovement(
                5,
                "ADD",
                5,
                "Você adicionou créditos",
                operation_id=uuid.uuid1(),
                id=uuid.uuid1(),
            )
        )
        sut = CreditAccount(
            company_id=company_id,
            credit_state_list=[expired_credit],
            reference_date=reference_date,
        )
        sut._reference_date = date(2022, 11, 1)
        assert sut.get_balance() == 0
        sut._reference_date = date(2022, 11, 1)
        sut.renew()
        assert sut.get_balance() == 5
