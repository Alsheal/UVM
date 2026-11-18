import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from uvm.assembler import SIZE_MESSAGE, main
from uvm.encoder import encode_instruction
from uvm.listing import format_command
from uvm.parser import parse_program
from uvm.spec import COMMAND_SIZE_BYTES

EXAMPLE_PATH = Path(__file__).resolve().parent.parent / "examples" / "spec_tests.asm"
OUTPUT_NAME = "program.bin"

SPEC_BYTES = (
    ("ldc r25, 638", (0xD6, 0x4F, 0x00, 0x00, 0xC8, 0x00)),
    ("ld r10, 28", (0x40, 0xE1, 0x00, 0x00, 0x00, 0x00)),
    ("st r54, r15", (0xD0, 0x7E, 0x00, 0x00, 0x00, 0x00)),
    ("ror r55, 454", (0xE4, 0x36, 0x0E, 0x00, 0x00, 0x00)),
)
EXPECTED_BINARY = b"".join(bytes(expected) for _, expected in SPEC_BYTES)
EXPECTED_SIZE = COMMAND_SIZE_BYTES * len(SPEC_BYTES)
EXPECTED_LISTING = [
    "0xD6, 0x4F, 0x00, 0x00, 0xC8, 0x00",
    "0x40, 0xE1, 0x00, 0x00, 0x00, 0x00",
    "0xD0, 0x7E, 0x00, 0x00, 0x00, 0x00",
    "0xE4, 0x36, 0x0E, 0x00, 0x00, 0x00",
]


class EncodingTest(unittest.TestCase):
    def test_each_command_matches_specification_bytes(self):
        for source, expected in SPEC_BYTES:
            with self.subTest(source=source):
                (instruction,) = parse_program(source)
                self.assertEqual(encode_instruction(instruction), bytes(expected))

    def test_every_command_has_fixed_size(self):
        for source, _ in SPEC_BYTES:
            with self.subTest(source=source):
                (instruction,) = parse_program(source)
                self.assertEqual(len(encode_instruction(instruction)), COMMAND_SIZE_BYTES)

    def test_command_is_formatted_as_in_specification(self):
        command = bytes(SPEC_BYTES[0][1])
        self.assertEqual(format_command(command), EXPECTED_LISTING[0])


class AssemblerCliTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.output = Path(directory.name) / OUTPUT_NAME

    def run_cli(self, *extra_args: str) -> tuple[int, list[str]]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main([str(EXAMPLE_PATH), str(self.output), *extra_args])
        return exit_code, buffer.getvalue().splitlines()

    def test_binary_file_matches_specification(self):
        self.run_cli()
        self.assertEqual(self.output.read_bytes(), EXPECTED_BINARY)

    def test_size_is_printed(self):
        _, lines = self.run_cli()
        self.assertEqual(lines, [SIZE_MESSAGE.format(size=EXPECTED_SIZE)])

    def test_test_mode_prints_bytes_after_size(self):
        _, lines = self.run_cli("--test")
        self.assertEqual(lines[1:], EXPECTED_LISTING)

    def test_invalid_program_returns_error_code(self):
        broken = self.output.with_suffix(".asm")
        broken.write_text("nop", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            exit_code = main([str(broken), str(self.output)])
        self.assertNotEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()