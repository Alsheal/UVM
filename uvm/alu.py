"""АЛУ УВМ: вычислительные операции над словами."""

from uvm.memory import WORD_BITS, WORD_MASK


def rotate_right(value: int, shift: int) -> int:
    """Побитовый циклический сдвиг слова вправо."""
    amount = shift % WORD_BITS
    rotated_out = (value << (WORD_BITS - amount)) & WORD_MASK
    return (value >> amount) | rotated_out