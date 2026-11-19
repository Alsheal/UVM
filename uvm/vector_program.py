"""Генератор программ поэлементного ror над двумя векторами."""

from pathlib import Path

VECTOR_LENGTH = 7
FIRST_ADDRESS_A = 0
FIRST_ADDRESS_B = 10
FIRST_ADDRESS_RESULT = 20

REGISTER_ADDRESS = 0
REGISTER_VALUE = 1
REGISTER_ELEMENT = 2
REGISTER_RESULT_ADDRESS = 3

EXAMPLES_DIRECTORY = Path(__file__).resolve().parent.parent / "examples"
FILE_NAME_TEMPLATE = "vector_ror_{number}.asm"
FILE_ENCODING = "utf-8"

EXAMPLES = (
    (
        (1, 2, 4, 8, 16, 32, 64),
        (1, 1, 1, 1, 1, 1, 1),
    ),
    (
        (1, 1, 1, 1, 1, 1, 1),
        (0, 1, 4, 8, 16, 31, 32),
    ),
    (
        (0x12345678,) * VECTOR_LENGTH,
        (4, 8, 12, 16, 20, 24, 28),
    ),
)


def store_constant(address: int, value: int) -> list[str]:
    """Записывает константу в память данных по адресу."""
    return [
        f"ldc r{REGISTER_ADDRESS}, {address}",
        f"ldc r{REGISTER_VALUE}, {value}",
        f"st r{REGISTER_ADDRESS}, r{REGISTER_VALUE}",
    ]


def init_vector(first_address: int, values: tuple[int, ...]) -> list[str]:
    lines = []
    for offset, value in enumerate(values):
        lines += store_constant(first_address + offset, value)
    return lines


def process_element(index: int) -> list[str]:
    return [
        f"ld r{REGISTER_ELEMENT}, {FIRST_ADDRESS_A + index}",
        f"ror r{REGISTER_ELEMENT}, {FIRST_ADDRESS_B + index}",
        f"ldc r{REGISTER_RESULT_ADDRESS}, {FIRST_ADDRESS_RESULT + index}",
        f"st r{REGISTER_RESULT_ADDRESS}, r{REGISTER_ELEMENT}",
    ]


def check_length(name: str, values: tuple[int, ...]) -> None:
    if len(values) != VECTOR_LENGTH:
        raise ValueError(
            f"вектор {name} должен содержать {VECTOR_LENGTH} элементов, "
            f"получено {len(values)}"
        )


def build_source(vector_a: tuple[int, ...], vector_b: tuple[int, ...]) -> str:
    check_length("A", vector_a)
    check_length("B", vector_b)
    lines = [
        f"; Вектор A: mem[{FIRST_ADDRESS_A}..{FIRST_ADDRESS_A + VECTOR_LENGTH - 1}]",
        f"; Вектор B: mem[{FIRST_ADDRESS_B}..{FIRST_ADDRESS_B + VECTOR_LENGTH - 1}]",
        f"; Результат: mem[{FIRST_ADDRESS_RESULT}.."
        f"{FIRST_ADDRESS_RESULT + VECTOR_LENGTH - 1}]",
        *init_vector(FIRST_ADDRESS_A, vector_a),
        *init_vector(FIRST_ADDRESS_B, vector_b),
    ]
    for index in range(VECTOR_LENGTH):
        lines += process_element(index)
    return "\n".join(lines) + "\n"


def example_path(directory: Path, number: int) -> Path:
    return directory / FILE_NAME_TEMPLATE.format(number=number)


def write_examples(directory: Path) -> list[Path]:
    paths = []
    for number, (vector_a, vector_b) in enumerate(EXAMPLES, start=1):
        path = example_path(directory, number)
        path.write_text(build_source(vector_a, vector_b), encoding=FILE_ENCODING)
        paths.append(path)
    return paths


def main() -> None:
    for path in write_examples(EXAMPLES_DIRECTORY):
        print(path)


if __name__ == "__main__":
    main()