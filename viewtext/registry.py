from typing import Callable


class BaseFieldRegistry:
    def __init__(self) -> None:
        self._fields: dict[str, Callable] = {}

    def register(self, name: str, getter: Callable) -> None:
        self._fields[name] = getter

    def get(self, name: str) -> Callable:
        if name not in self._fields:
            raise ValueError(f"Unknown field: {name}")
        return self._fields[name]

    def has_field(self, name: str) -> bool:
        return name in self._fields
