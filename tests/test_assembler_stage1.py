import unittest
from pathlib import Path

from uvm.parser import AssemblerError, parse_program

ROOT_DIRECTORY = Path(__file__).resolve().parent.parent
EXAMPLE_PATH = ROOT_DIRECTORY / "examples" / "spec_tests.asm"
SOURCE_ENCODING = "utf-8"

SPEC_CASES = (
    ("ldc r25, 638", {"A": 22, "B": 638, "C": 25}),
    ("ld r10, 28", {"A": 0, "B": 10, "C": 28}),
    ("st r54, r15", {"A": 16, "B": 54, "C": 15}),
    ("ror r55, 454", {"A": 4, "B": 55, "C": 454}),
)

INVALID_SOURCES = (
    "nop",
    "ldc r1",
    "ld 5, 28",
    "ld r64, 0",
    "ldc r1, 1073741824",
    "ror r1, -1",
)


class SpecCasesTest(unittest.TestCase):
    def test_each_command_matches_specification(self):
        for source, expected in SPEC_CASES:
            with self.subTest(source=source):
                (instruction,) = parse_program(source)
                self.assertEqual(instruction.values, expected)

    def test_example_file_matches_specification(self):
        text = EXAMPLE_PATH.read_text(encoding=SOURCE_ENCODING)
        actual = [instruction.values for instruction in parse_program(text)]
        self.assertEqual(actual, [expected for _, expected in SPEC_CASES])

    def test_fields_are_formatted_as_in_specification(self):
        (instruction,) = parse_program("ldc r25, 638")
        self.assertEqual(instruction.format_fields(), "A=22, B=638, C=25")

    def test_comments_and_empty_lines_are_ignored(self):
        self.assertEqual(parse_program("; только комментарий\n\n"), [])


class InvalidProgramTest(unittest.TestCase):
    def test_invalid_sources_raise_assembler_error(self):
        for source in INVALID_SOURCES:
            with self.subTest(source=source):
                with self.assertRaises(AssemblerError):
                    parse_program(source)


if __name__ == "__main__":
    unittest.main()
