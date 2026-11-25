"""Модель памяти УВМ: массив слов фиксированного размера."""

from uvm.errors import ExecutionError

WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1
INITIAL_WORD = 0


class Memory:
    def __init__(self, size: int) -> None:
        self._words = [INITIAL_WORD] * size

    def __len__(self) -> int:
        return len(self._words)

    def _checked(self, address: int) -> int:
        if not 0 <= address < len(self._words):
            raise ExecutionError(
                f"адрес {address} вне диапазона 0..{len(self._words) - 1}"
            )
        return address

    def read(self, address: int) -> int:
        return self._words[self._checked(address)]

    def write(self, address: int, value: int) -> None:
        self._words[self._checked(address)] = value & WORD_MASK