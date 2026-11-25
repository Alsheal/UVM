"""Выполнение команд УВМ: таблица обработчиков и основной цикл."""

from typing import Callable

from uvm.alu import rotate_right
from uvm.decoder import decode_command
from uvm.errors import ExecutionError
from uvm.machine import Machine
from uvm.model import Instruction
from uvm.spec import (
    LOAD_CONST_B,
    LOAD_CONST_C,
    OPCODE_LOAD_CONST,
    OPCODE_READ,
    OPCODE_ROR,
    OPCODE_WRITE,
    READ_B,
    READ_C,
    ROR_B,
    ROR_C,
    WRITE_B,
    WRITE_C,
)

Handler = Callable[[Machine, dict[str, int]], None]


def execute_load_const(machine: Machine, values: dict[str, int]) -> None:
    machine.registers.write(
        values[LOAD_CONST_C.name], values[LOAD_CONST_B.name]
    )


def execute_read(machine: Machine, values: dict[str, int]) -> None:
    value = machine.data_memory.read(values[READ_C.name])
    machine.registers.write(values[READ_B.name], value)


def execute_write(machine: Machine, values: dict[str, int]) -> None:
    address = machine.registers.read(values[WRITE_B.name])
    value = machine.registers.read(values[WRITE_C.name])
    machine.data_memory.write(address, value)


def execute_ror(machine: Machine, values: dict[str, int]) -> None:
    value = machine.registers.read(values[ROR_B.name])
    shift = machine.data_memory.read(values[ROR_C.name])
    machine.registers.write(values[ROR_B.name], rotate_right(value, shift))


HANDLERS: dict[int, Handler] = {
    OPCODE_LOAD_CONST: execute_load_const,
    OPCODE_READ: execute_read,
    OPCODE_WRITE: execute_write,
    OPCODE_ROR: execute_ror,
}


def find_handler(instruction: Instruction) -> Handler:
    handler = HANDLERS.get(instruction.spec.opcode)
    if handler is None:
        raise ExecutionError(
            f"команда '{instruction.spec.mnemonic}' не поддерживается"
        )
    return handler


def execute(machine: Machine, instruction: Instruction) -> None:
    find_handler(instruction)(machine, instruction.values)


def run(machine: Machine) -> None:
    for command in machine.code_memory:
        execute(machine, decode_command(command))
