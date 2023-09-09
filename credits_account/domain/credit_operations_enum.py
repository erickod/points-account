import enum
from typing import Tuple, List


@enum.unique
class OperationCreditsEnum(enum.Enum):
    ADD = "adicionou"
    CONSUME = 'consumiu'
    EXPIRE = "expirou"
    REFUND = "extornou"
    RENEW = "renovou"

    @classmethod
    def as_tuple(cls) -> List[Tuple[str, str]]:
        return [(each.name, each.value) for each in OperationCreditsEnum]
