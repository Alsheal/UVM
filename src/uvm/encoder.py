"""Трансляция промежуточного представления в машинный код."""

from functools import reduce
from operator import or_

from uvm.model import Instruction
from uvm.spec import COMMAND_SIZE_BYTES, Field

BYTE_ORDER = "little"
EMPTY_WORD = 0


def shift_field(instruction: Instruction, field: Field) -> int:
    return instruction.values[field.name] << field.offset


def pack_word(instruction: Instruction) -> int:
    shifted = (
        shift_field(instruction, field) for field in instruction.spec.fields
    )
    return reduce(or_, shifted, EMPTY_WORD)


def encode_instruction(instruction: Instruction) -> bytes:
    return pack_word(instruction).to_bytes(COMMAND_SIZE_BYTES, BYTE_ORDER)


def encode_program(instructions: list[Instruction]) -> list[bytes]:
    return [encode_instruction(instruction) for instruction in instructions]
