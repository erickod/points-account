from uuid import uuid1

from credits_account.domain.entities.credit_account import CreditAccount

sut = CreditAccount(company_id=uuid1(), credit_state_list=[])
sut.add(5, "asdf", "subscription")
sut.add(5, "asdfasfd", "subscription")
sut.consume(6, "asdfasdf")
print(sut)
