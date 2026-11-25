"""Состояние УВМ: память команд, регистры и память данных."""

from dataclasses import dataclass, field

from uvm.memory import Memory
from uvm.spec import READ_B, READ_C

REGISTER_COUNT = READ_B.max_value + 1
DATA_MEMORY_SIZE = READ_C.max_value + 1


@dataclass
class Machine:
    code_memory: list[bytes]
    registers: Memory = field(default_factory=lambda: Memory(REGISTER_COUNT))
    data_memory: Memory = field(
        default_factory=lambda: Memory(DATA_MEMORY_SIZE)
    )
