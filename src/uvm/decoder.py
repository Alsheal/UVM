"""Перевод машинного кода в промежуточное представление."""

from uvm.encoder import BYTE_ORDER
from uvm.errors import ExecutionError
from uvm.model import Instruction
from uvm.spec import (
    COMMAND_SIZE_BYTES,
    COMMANDS_BY_OPCODE,
    OPCODE_FIELD,
    CommandSpec,
    Field,
)


def extract_field(word: int, field: Field) -> int:
    return (word >> field.offset) & field.max_value


def find_command_by_opcode(opcode: int) -> CommandSpec:
    command = COMMANDS_BY_OPCODE.get(opcode)
    if command is None:
        raise ExecutionError(f"неизвестный код операции {opcode}")
    return command


def decode_command(command: bytes) -> Instruction:
    word = int.from_bytes(command, BYTE_ORDER)
    spec = find_command_by_opcode(extract_field(word, OPCODE_FIELD))
    values = {field.name: extract_field(word, field) for field in spec.fields}
    return Instruction(spec=spec, values=values)


def split_commands(binary: bytes) -> list[bytes]:
    if len(binary) % COMMAND_SIZE_BYTES != 0:
        raise ExecutionError(
            f"размер программы {len(binary)} байт не кратен "
            f"размеру команды {COMMAND_SIZE_BYTES}"
        )
    return [
        binary[start : start + COMMAND_SIZE_BYTES]
        for start in range(0, len(binary), COMMAND_SIZE_BYTES)
    ]
