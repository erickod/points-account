from dataclasses import dataclass


@dataclass(frozen=True)
class MovementTarget:
    object_type: str
    object_id: str
