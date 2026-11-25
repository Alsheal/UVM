"""Трансляция текста на языке ассемблера в промежуточное представление."""

import re

from uvm.model import Instruction
from uvm.spec import (
    COMMANDS_BY_MNEMONIC,
    OPCODE_FIELD,
    CommandSpec,
    Field,
    Operand,
    OperandKind,
)

COMMENT_PREFIX = ";"
OPERAND_SEPARATOR = ","
FIRST_LINE_NUMBER = 1
NUMBER_BASE_AUTO = 0

REGISTER_PATTERN = re.compile(r"r(\d+)")


class AssemblerError(Exception):
    """Ошибка в тексте программы на языке ассемблера."""


def parse_register(token: str) -> int:
    match = REGISTER_PATTERN.fullmatch(token)
    if match is None:
        raise AssemblerError(f"ожидался регистр вида r<N>, получено '{token}'")
    return int(match.group(1))


def parse_number(token: str) -> int:
    """Разбирает число: десятичное, 0x.. или 0b..

    Основание определяется автоматически (int с основанием 0).
    """
    try:
        return int(token, NUMBER_BASE_AUTO)
    except ValueError:
        raise AssemblerError(f"ожидалось число, получено '{token}'") from None


OPERAND_PARSERS = {
    OperandKind.REGISTER: parse_register,
    OperandKind.NUMBER: parse_number,
}


def ensure_in_range(value: int, field: Field) -> int:
    if not 0 <= value <= field.max_value:
        raise AssemblerError(
            f"значение {value} не помещается в поле {field.name} "
            f"(допустимо 0..{field.max_value})"
        )
    return value


def parse_operand(token: str, operand: Operand) -> int:
    value = OPERAND_PARSERS[operand.kind](token)
    return ensure_in_range(value, operand.field)


def strip_comment(line: str) -> str:
    return line.split(COMMENT_PREFIX, 1)[0].strip()


def split_statement(statement: str) -> tuple[str, list[str]]:
    parts = statement.split(maxsplit=1)
    mnemonic = parts[0].lower()
    operand_text = "".join(parts[1:])
    tokens = operand_text.split(OPERAND_SEPARATOR) if operand_text else []
    return mnemonic, [token.strip() for token in tokens]


def find_command(mnemonic: str) -> CommandSpec:
    command = COMMANDS_BY_MNEMONIC.get(mnemonic)
    if command is None:
        raise AssemblerError(f"неизвестная команда '{mnemonic}'")
    return command


def ensure_operand_count(command: CommandSpec, tokens: list[str]) -> None:
    if len(tokens) != len(command.operands):
        raise AssemblerError(
            f"команда '{command.mnemonic}' принимает операндов: "
            f"{len(command.operands)}, получено: {len(tokens)}"
        )


def build_instruction(command: CommandSpec, tokens: list[str]) -> Instruction:
    ensure_operand_count(command, tokens)
    parsed = {OPCODE_FIELD.name: command.opcode}
    parsed.update(
        {
            operand.field.name: parse_operand(token, operand)
            for operand, token in zip(command.operands, tokens)
        }
    )
    ordered = {field.name: parsed[field.name] for field in command.fields}
    return Instruction(spec=command, values=ordered)


def parse_statement(statement: str) -> Instruction:
    mnemonic, tokens = split_statement(statement)
    return build_instruction(find_command(mnemonic), tokens)


def parse_numbered_statement(line_number: int, statement: str) -> Instruction:
    try:
        return parse_statement(statement)
    except AssemblerError as error:
        raise AssemblerError(f"строка {line_number}: {error}") from error


def parse_program(source: str) -> list[Instruction]:
    numbered = enumerate(source.splitlines(), start=FIRST_LINE_NUMBER)
    statements = [(number, strip_comment(line)) for number, line in numbered]
    return [
        parse_numbered_statement(number, statement)
        for number, statement in statements
        if statement
    ]
