import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from uvm import assembler, interpreter
from uvm.decoder import decode_command, split_commands
from uvm.dump import build_dump
from uvm.encoder import encode_program
from uvm.errors import ExecutionError
from uvm.executor import run
from uvm.machine import DATA_MEMORY_SIZE, Machine
from uvm.parser import parse_program
from uvm.spec import COMMAND_SIZE_BYTES

COPY_ARRAY_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "copy_array.asm"
)
FILE_ENCODING = "utf-8"

SOURCE_FIRST = 100
DESTINATION_FIRST = 200
ARRAY_VALUES = (11, 22, 33, 44, 55)
UNKNOWN_OPCODE_COMMAND = bytes([31, 0, 0, 0, 0, 0])

SPEC_DECODED = (
    (bytes([0xD6, 0x4F, 0x00, 0x00, 0xC8, 0x00]), {"A": 22, "B": 638, "C": 25}),
    (bytes([0x40, 0xE1, 0x00, 0x00, 0x00, 0x00]), {"A": 0, "B": 10, "C": 28}),
    (bytes([0xD0, 0x7E, 0x00, 0x00, 0x00, 0x00]), {"A": 16, "B": 54, "C": 15}),
    (bytes([0xE4, 0x36, 0x0E, 0x00, 0x00, 0x00]), {"A": 4, "B": 55, "C": 454}),
)


def expected_dump(first: int) -> dict[str, int]:
    return {str(first + index): value for index, value in enumerate(ARRAY_VALUES)}


def run_source(source: str) -> Machine:
    machine = Machine(code_memory=encode_program(parse_program(source)))
    run(machine)
    return machine


class DecodingTest(unittest.TestCase):
    def test_specification_bytes_decode_to_fields(self):
        for command, expected in SPEC_DECODED:
            with self.subTest(command=command):
                self.assertEqual(decode_command(command).values, expected)

    def test_unknown_opcode_is_rejected(self):
        with self.assertRaises(ExecutionError):
            decode_command(UNKNOWN_OPCODE_COMMAND)

    def test_binary_is_split_into_commands(self):
        commands = split_commands(bytes(COMMAND_SIZE_BYTES * 2))
        self.assertEqual(len(commands), 2)

    def test_partial_command_is_rejected(self):
        with self.assertRaises(ExecutionError):
            split_commands(bytes(COMMAND_SIZE_BYTES - 1))


class ExecutionTest(unittest.TestCase):
    def test_load_const_sets_register(self):
        machine = run_source("ldc r5, 638")
        self.assertEqual(machine.registers.read(5), 638)

    def test_write_stores_register_value_by_register_address(self):
        machine = run_source("ldc r0, 9\nldc r1, 42\nst r0, r1")
        self.assertEqual(machine.data_memory.read(9), 42)

    def test_read_loads_memory_value_into_register(self):
        machine = run_source("ldc r0, 50\nldc r1, 7\nst r0, r1\nld r2, 50")
        self.assertEqual(machine.registers.read(2), 7)

    def test_write_outside_data_memory_is_rejected(self):
        with self.assertRaises(ExecutionError):
            run_source(f"ldc r0, {DATA_MEMORY_SIZE}\nldc r1, 1\nst r0, r1")

    def test_code_memory_is_not_modified_by_execution(self):
        source = COPY_ARRAY_PATH.read_text(encoding=FILE_ENCODING)
        machine = run_source(source)
        self.assertEqual(machine.code_memory, encode_program(parse_program(source)))


class DumpRangeTest(unittest.TestCase):
    def test_reversed_range_is_rejected(self):
        machine = Machine(code_memory=[])
        with self.assertRaises(ExecutionError):
            build_dump(machine.data_memory, 5, 1)

    def test_range_outside_memory_is_rejected(self):
        machine = Machine(code_memory=[])
        with self.assertRaises(ExecutionError):
            build_dump(machine.data_memory, 0, DATA_MEMORY_SIZE)


class CopyArrayCliTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.binary = Path(directory.name) / "copy_array.bin"
        self.dump = Path(directory.name) / "dump.json"
        with redirect_stdout(io.StringIO()):
            assembler.main([str(COPY_ARRAY_PATH), str(self.binary)])

    def run_interpreter(self, first: int, last: int) -> int:
        arguments = [str(self.binary), str(self.dump)]
        arguments += ["--from", str(first), "--to", str(last)]
        with redirect_stderr(io.StringIO()):
            return interpreter.main(arguments)

    def read_dump(self) -> dict[str, int]:
        return json.loads(self.dump.read_text(encoding=FILE_ENCODING))

    def test_source_array_is_initialized(self):
        self.run_interpreter(SOURCE_FIRST, SOURCE_FIRST + len(ARRAY_VALUES) - 1)
        self.assertEqual(self.read_dump(), expected_dump(SOURCE_FIRST))

    def test_array_is_copied(self):
        self.run_interpreter(DESTINATION_FIRST, DESTINATION_FIRST + len(ARRAY_VALUES) - 1)
        self.assertEqual(self.read_dump(), expected_dump(DESTINATION_FIRST))

    def test_invalid_range_returns_error_and_writes_nothing(self):
        exit_code = self.run_interpreter(5, 1)
        self.assertNotEqual(exit_code, 0)
        self.assertFalse(self.dump.exists())

    def test_corrupted_binary_returns_error(self):
        self.binary.write_bytes(bytes(COMMAND_SIZE_BYTES - 1))
        self.assertNotEqual(self.run_interpreter(0, 1), 0)


if __name__ == "__main__":
    unittest.main()