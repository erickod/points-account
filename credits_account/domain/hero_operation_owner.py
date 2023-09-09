from uuid import UUID
import dataclasses


@dataclasses.dataclass
class OperationOwner:
    name: str
    email: str
    id:UUID


HERO_OPERATION_OWNER = OperationOwner(
    id=UUID("9bdafc83-2188-4c18-a638-41255372553b"),
    name="herobot",
    email="herobot@companyhero.com",
)