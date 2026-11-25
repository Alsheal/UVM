"""CLI-приложение интерпретатора УВМ."""

import argparse
import sys
from pathlib import Path

from uvm.decoder import split_commands
from uvm.dump import build_dump, write_dump
from uvm.errors import ExecutionError
from uvm.executor import run
from uvm.machine import Machine

EXIT_OK = 0
EXIT_ERROR = 1


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Интерпретатор учебной виртуальной машины"
    )
    parser.add_argument(
        "binary", type=Path, help="путь к бинарному файлу программы"
    )
    parser.add_argument(
        "dump", type=Path, help="путь к файлу дампа памяти (JSON)"
    )
    parser.add_argument(
        "--from",
        dest="first",
        type=int,
        required=True,
        help="первый адрес памяти данных для дампа",
    )
    parser.add_argument(
        "--to",
        dest="last",
        type=int,
        required=True,
        help="последний адрес памяти данных для дампа (включительно)",
    )
    return parser


def load_machine(path: Path) -> Machine:
    return Machine(code_memory=split_commands(path.read_bytes()))


def interpret(binary: Path, dump: Path, first: int, last: int) -> None:
    machine = load_machine(binary)
    run(machine)
    write_dump(dump, build_dump(machine.data_memory, first, last))


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        interpret(args.binary, args.dump, args.first, args.last)
    except (OSError, ExecutionError) as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
