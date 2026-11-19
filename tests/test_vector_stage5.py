import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from uvm import assembler, interpreter
from uvm.alu import rotate_right
from uvm.dump import build_dump
from uvm.encoder import encode_program
from uvm.executor import run
from uvm.machine import Machine
from uvm.parser import parse_program
from uvm.vector_program import (
    EXAMPLES,
    EXAMPLES_DIRECTORY,
    FIRST_ADDRESS_A,
    FIRST_ADDRESS_B,
    FIRST_ADDRESS_RESULT,
    VECTOR_LENGTH,
    build_source,
    example_path,
)

FILE_ENCODING = "utf-8"

EXPECTED_RESULTS = (
    (0x80000000, 0x1, 0x2, 0x4, 0x8, 0x10, 0x20),
    (0x1, 0x80000000, 0x10000000, 0x1000000, 0x10000, 0x2, 0x1),
    (
        0x81234567,
        0x78123456,
        0x67812345,
        0x56781234,
        0x45678123,
        0x34567812,
        0x23456781,
    ),
)


def vector_dump(machine: Machine, first_address: int) -> dict[str, int]:
    last_address = first_address + VECTOR_LENGTH - 1
    return build_dump(machine.data_memory, first_address, last_address)


def expected_dump(first_address: int, values: tuple[int, ...]) -> dict[str, int]:
    return {str(first_address + index): value for index, value in enumerate(values)}


def run_example(number: int) -> Machine:
    source = example_path(EXAMPLES_DIRECTORY, number).read_text(encoding=FILE_ENCODING)
    machine = Machine(code_memory=encode_program(parse_program(source)))
    run(machine)
    return machine


class VectorExamplesTest(unittest.TestCase):
    def test_result_matches_expected_values(self):
        for number, expected in enumerate(EXPECTED_RESULTS, start=1):
            with self.subTest(example=number):
                machine = run_example(number)
                self.assertEqual(
                    vector_dump(machine, FIRST_ADDRESS_RESULT),
                    expected_dump(FIRST_ADDRESS_RESULT, expected),
                )

    def test_expected_values_match_alu(self):
        for (vector_a, vector_b), expected in zip(EXAMPLES, EXPECTED_RESULTS):
            computed = tuple(rotate_right(a, b) for a, b in zip(vector_a, vector_b))
            with self.subTest(vector_a=vector_a):
                self.assertEqual(computed, expected)

    def test_input_vectors_are_not_modified(self):
        for number, (vector_a, vector_b) in enumerate(EXAMPLES, start=1):
            with self.subTest(example=number):
                machine = run_example(number)
                self.assertEqual(
                    vector_dump(machine, FIRST_ADDRESS_A),
                    expected_dump(FIRST_ADDRESS_A, vector_a),
                )
                self.assertEqual(
                    vector_dump(machine, FIRST_ADDRESS_B),
                    expected_dump(FIRST_ADDRESS_B, vector_b),
                )

    def test_committed_programs_match_generator(self):
        for number, (vector_a, vector_b) in enumerate(EXAMPLES, start=1):
            with self.subTest(example=number):
                text = example_path(EXAMPLES_DIRECTORY, number).read_text(
                    encoding=FILE_ENCODING
                )
                self.assertEqual(text, build_source(vector_a, vector_b))

    def test_wrong_vector_length_is_rejected(self):
        with self.assertRaises(ValueError):
            build_source((1,), (1,) * VECTOR_LENGTH)


class VectorCliTest(unittest.TestCase):
    def test_dump_file_contains_result_vector(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "vector.bin"
            dump = Path(directory) / "dump.json"
            source = example_path(EXAMPLES_DIRECTORY, 3)
            with redirect_stdout(io.StringIO()):
                assembler.main([str(source), str(binary)])
            last = FIRST_ADDRESS_RESULT + VECTOR_LENGTH - 1
            arguments = [str(binary), str(dump)]
            arguments += ["--from", str(FIRST_ADDRESS_RESULT), "--to", str(last)]
            with redirect_stderr(io.StringIO()):
                interpreter.main(arguments)
            result = json.loads(dump.read_text(encoding=FILE_ENCODING))
        self.assertEqual(
            result, expected_dump(FIRST_ADDRESS_RESULT, EXPECTED_RESULTS[2])
        )


if __name__ == "__main__":
    unittest.main()