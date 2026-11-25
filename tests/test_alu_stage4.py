import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from uvm import assembler, interpreter
from uvm.alu import rotate_right
from uvm.encoder import encode_program
from uvm.executor import run
from uvm.machine import Machine
from uvm.memory import WORD_BITS, WORD_MASK
from uvm.parser import parse_program

ROOT_DIRECTORY = Path(__file__).resolve().parent.parent
DEMO_PATH = ROOT_DIRECTORY / "examples" / "ror_demo.asm"

RESULT_FIRST = 20
RESULT_LAST = 21
EXPECTED_DEMO_DUMP = {"20": 0x81234567, "21": 0x80000000}

ROTATE_CASES = (
    (0x12345678, 4, 0x81234567),
    (0x00000001, 1, 0x80000000),
    (0x80000000, 31, 0x00000001),
    (0x12345678, 0, 0x12345678),
    (0x12345678, WORD_BITS, 0x12345678),
    (0x12345678, WORD_BITS + 4, 0x81234567),
    (WORD_MASK, 5, WORD_MASK),
)


def run_source(source: str) -> Machine:
    machine = Machine(code_memory=encode_program(parse_program(source)))
    run(machine)
    return machine


class RotateRightTest(unittest.TestCase):
    def test_known_values(self):
        for value, shift, expected in ROTATE_CASES:
            with self.subTest(value=hex(value), shift=shift):
                self.assertEqual(rotate_right(value, shift), expected)

    def test_inverse_rotation_restores_value(self):
        value = 0x12345678
        for shift in range(WORD_BITS):
            with self.subTest(shift=shift):
                rotated = rotate_right(value, shift)
                self.assertEqual(
                    rotate_right(rotated, WORD_BITS - shift), value
                )


class RotateRightCommandTest(unittest.TestCase):
    SOURCE = (
        "ldc r0, 10\n"
        "ldc r1, 4\n"
        "st r0, r1\n"
        "ldc r2, 305419896\n"
        "ror r2, 10\n"
    )

    def test_command_rotates_register_by_memory_value(self):
        machine = run_source(self.SOURCE)
        self.assertEqual(machine.registers.read(2), 0x81234567)

    def test_command_does_not_change_shift_in_memory(self):
        machine = run_source(self.SOURCE)
        self.assertEqual(machine.data_memory.read(10), 4)

    def test_uninitialized_memory_means_zero_shift(self):
        machine = run_source("ldc r0, 77\nror r0, 500")
        self.assertEqual(machine.registers.read(0), 77)


class DemoProgramTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.binary = Path(directory.name) / "ror_demo.bin"
        self.dump = Path(directory.name) / "dump.json"
        with redirect_stdout(io.StringIO()):
            assembler.main([str(DEMO_PATH), str(self.binary)])

    def test_results_are_stored_in_memory(self):
        arguments = [str(self.binary), str(self.dump)]
        arguments += ["--from", str(RESULT_FIRST), "--to", str(RESULT_LAST)]
        with redirect_stderr(io.StringIO()):
            interpreter.main(arguments)
        result = json.loads(self.dump.read_text(encoding=FILE_ENCODING))
        self.assertEqual(result, EXPECTED_DEMO_DUMP)


if __name__ == "__main__":
    unittest.main()
