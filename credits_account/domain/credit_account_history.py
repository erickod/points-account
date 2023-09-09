from typing import Any, Dict, List, Set, Tuple
from itertools import chain


class CreditAccountHistory:
    def __init__(self) -> None:
        #TODO: Create a base class to operations and assign the new type below
        self._operations:Dict[str, Any] = {}
    
    def list_operation_types(self) -> Tuple[str, ...]:
        return tuple(self._operations)
    
    def register_operation(self, *operations: Any) -> None:
        for operation in operations:
            operation_type = operation.type.upper()
            if operation_type not in self._operations:
                self._operations[operation_type] = []
            self._operations[operation_type].append(operation)
    
    def get_operations(self, operation_type:str) -> List[Any]:
        return self._operations.get(operation_type.upper(), [])
    
    def __iter__(self) -> Any:
        for operation_list in self._operations.values():
            for operation in operation_list:
                yield operation
    
    def __contains__(self, other:Any) -> bool:
        operation_list = []
        for operation_type_list in self._operations.values():
            operation_list.extend(operation_type_list)
        credit_list = [credit for operation in operation_list for credit in operation.credits]
        if other in chain(operation_list, credit_list):
            return True
        return False

