import uuid
from unittest import TestCase

from credits_account.domain.entities.credit_account import CreditAccount

company_id = uuid.uuid1()


class TestCreditAccount(TestCase):
    def setUp(self) -> None:
        pass

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
