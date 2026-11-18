"""CLI-приложение ассемблера УВМ."""

import argparse
import sys
from pathlib import Path

from uvm.model import Instruction
from uvm.parser import AssemblerError, parse_program

SOURCE_ENCODING = "utf-8"
EXIT_OK = 0
EXIT_ERROR = 1


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ассемблер учебной виртуальной машины")
    parser.add_argument("source", type=Path, help="путь к исходному файлу с программой")
    parser.add_argument("output", type=Path, help="путь к двоичному файлу-результату")
    parser.add_argument(
        "--test",
        action="store_true",
        help="режим тестирования: вывести внутреннее представление программы",
    )
    return parser


def read_source(path: Path) -> str:
    return path.read_text(encoding=SOURCE_ENCODING)


def print_intermediate(instructions: list[Instruction]) -> None:
    for instruction in instructions:
        print(instruction.format_fields())


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        instructions = parse_program(read_source(args.source))
    except (OSError, AssemblerError) as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    if args.test:
        print_intermediate(instructions)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())