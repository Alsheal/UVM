"""CLI-приложение ассемблера УВМ."""

import argparse
import sys
from pathlib import Path

from uvm.encoder import encode_program
from uvm.listing import format_program
from uvm.parser import AssemblerError, parse_program

SOURCE_ENCODING = "utf-8"
EXIT_OK = 0
EXIT_ERROR = 1
SIZE_MESSAGE = "Размер двоичного файла (байт): {size}"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины"
    )
    parser.add_argument(
        "source", type=Path, help="путь к исходному файлу с программой"
    )
    parser.add_argument(
        "output", type=Path, help="путь к двоичному файлу-результату"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="режим тестирования: вывести машинный код в байтовом формате",
    )
    return parser


def read_source(path: Path) -> str:
    return path.read_text(encoding=SOURCE_ENCODING)


def write_binary(path: Path, commands: list[bytes]) -> int:
    """Записывает машинный код в файл и возвращает число записанных байт."""
    return path.write_bytes(b"".join(commands))


def assemble(source: Path, output: Path) -> tuple[list[bytes], int]:
    commands = encode_program(parse_program(read_source(source)))
    return commands, write_binary(output, commands)


def print_listing(commands: list[bytes]) -> None:
    for line in format_program(commands):
        print(line)


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        commands, size = assemble(args.source, args.output)
    except (OSError, AssemblerError) as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(SIZE_MESSAGE.format(size=size))
    if args.test:
        print_listing(commands)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
