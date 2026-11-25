"""Промежуточное представление программы."""

from dataclasses import dataclass

from uvm.spec import CommandSpec

FIELDS_SEPARATOR = ", "


@dataclass(frozen=True)
class Instruction:
    """Команда: спецификация и значения полей в порядке A, B, C."""

    spec: CommandSpec
    values: dict[str, int]

    def format_fields(self) -> str:
        return FIELDS_SEPARATOR.join(
            f"{name}={value}" for name, value in self.values.items()
        )
