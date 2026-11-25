"""Дамп памяти УВМ в формате JSON."""

import json
from pathlib import Path

from uvm.errors import ExecutionError
from uvm.memory import Memory

JSON_INDENT = 2
DUMP_ENCODING = "utf-8"


def build_dump(memory: Memory, first: int, last: int) -> dict[str, int]:
    """Значения ячеек с адресами first..last включительно."""
    if first > last:
        raise ExecutionError(f"начало диапазона {first} больше конца {last}")
    return {
        str(address): memory.read(address) for address in range(first, last + 1)
    }


def write_dump(path: Path, dump: dict[str, int]) -> None:
    path.write_text(
        json.dumps(dump, indent=JSON_INDENT), encoding=DUMP_ENCODING
    )
