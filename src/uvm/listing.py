"""Текстовое представление машинного кода."""

BYTE_FORMAT = "0x{:02X}"
BYTES_SEPARATOR = ", "


def format_command(command: bytes) -> str:
    return BYTES_SEPARATOR.join(BYTE_FORMAT.format(byte) for byte in command)


def format_program(commands: list[bytes]) -> list[str]:
    return [format_command(command) for command in commands]