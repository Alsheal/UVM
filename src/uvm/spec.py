"""Описание архитектуры УВМ: поля, операнды и команды."""

from dataclasses import dataclass
from enum import Enum

COMMAND_SIZE_BYTES = 6

OPCODE_READ = 0
OPCODE_ROR = 4
OPCODE_WRITE = 16
OPCODE_LOAD_CONST = 22

MNEMONIC_LOAD_CONST = "ldc"
MNEMONIC_READ = "ld"
MNEMONIC_WRITE = "st"
MNEMONIC_ROR = "ror"


class OperandKind(Enum):
    REGISTER = "register"
    NUMBER = "number"


@dataclass(frozen=True)
class Field:
    name: str
    offset: int
    width: int

    @property
    def max_value(self) -> int:
        return (1 << self.width) - 1


@dataclass(frozen=True)
class Operand:
    field: Field
    kind: OperandKind


OPCODE_FIELD = Field(name="A", offset=0, width=5)

LOAD_CONST_B = Field(name="B", offset=5, width=30)
LOAD_CONST_C = Field(name="C", offset=35, width=6)

READ_B = Field(name="B", offset=5, width=6)
READ_C = Field(name="C", offset=11, width=17)

WRITE_B = Field(name="B", offset=5, width=6)
WRITE_C = Field(name="C", offset=11, width=6)

ROR_B = Field(name="B", offset=5, width=6)
ROR_C = Field(name="C", offset=11, width=17)


@dataclass(frozen=True)
class CommandSpec:
    mnemonic: str
    opcode: int
    operands: tuple[Operand, ...]  # в порядке записи в ассемблере

    @property
    def fields(self) -> tuple[Field, ...]:
        """Все поля команды в порядке A, B, C (по возрастанию смещения)."""
        all_fields = (OPCODE_FIELD, *(operand.field for operand in self.operands))
        return tuple(sorted(all_fields, key=lambda field: field.offset))


LOAD_CONST = CommandSpec(
    mnemonic=MNEMONIC_LOAD_CONST,
    opcode=OPCODE_LOAD_CONST,
    operands=(
        Operand(LOAD_CONST_C, OperandKind.REGISTER),
        Operand(LOAD_CONST_B, OperandKind.NUMBER),
    ),
)

READ = CommandSpec(
    mnemonic=MNEMONIC_READ,
    opcode=OPCODE_READ,
    operands=(
        Operand(READ_B, OperandKind.REGISTER),
        Operand(READ_C, OperandKind.NUMBER),
    ),
)

WRITE = CommandSpec(
    mnemonic=MNEMONIC_WRITE,
    opcode=OPCODE_WRITE,
    operands=(
        Operand(WRITE_B, OperandKind.REGISTER),
        Operand(WRITE_C, OperandKind.REGISTER),
    ),
)

ROR = CommandSpec(
    mnemonic=MNEMONIC_ROR,
    opcode=OPCODE_ROR,
    operands=(
        Operand(ROR_B, OperandKind.REGISTER),
        Operand(ROR_C, OperandKind.NUMBER),
    ),
)

COMMANDS = (LOAD_CONST, READ, WRITE, ROR)
COMMANDS_BY_MNEMONIC = {command.mnemonic: command for command in COMMANDS}
COMMANDS_BY_OPCODE = {command.opcode: command for command in COMMANDS}