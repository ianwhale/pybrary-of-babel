"""Mimic a smarter person's implementation of the Library of Babel algorithm.

E.g.:
- https://github.com/cakenggt/Library-Of-Pybel
- https://github.com/louis-e/LibraryOfBabel-Python
"""

import math
import numpy as np
from typing import Optional
from pydantic import PrivateAttr

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class GeneratorConfig(BaseSettings):
    line_length: int = Field(
        default=79,
        description="Number of characters per line in the generated program.",
    )
    total_lines: int = Field(
        default=100,
        description="Total number of lines in the generated program.",
    )
    ascii_min: int = Field(
        default=32,
        description="Minimum ASCII value (inclusive) for readable characters.",
    )
    ascii_max: int = Field(
        default=126,
        description="Maximum ASCII value (inclusive) for readable characters.",
    )

    seed: Optional[int] = Field(
        default=None,
        description="Seed for deterministic random generation.",
    )

    _rng: Optional[np.random.Generator] = PrivateAttr(default=None)

    @property
    def rng(self) -> np.random.Generator:  # type: ignore
        """Return a random generator."""
        if self._rng is None:
            self._rng = np.random.default_rng(self.seed)
        return self._rng

    @computed_field
    def program_length(self) -> int:
        """Total number of characters in the program (line_length * total_lines)."""
        return self.line_length * self.total_lines

    @computed_field
    def ascii_range(self) -> int:
        """Number of distinct ASCII characters in the range (ascii_max - ascii_min + 1)."""
        return self.ascii_max - self.ascii_min + 1

    @computed_field
    def bytes_needed(self) -> int:
        """Number of bytes needed to represent the program (ceil(bits_needed / 8))."""
        return math.ceil(
            math.ceil(self.program_length * math.log2(self.ascii_range)) / 8  # type: ignore
        )


def hex_to_program_slow(
    hex_string: str,
    program_length: int,
    ascii_range: int,
    ascii_min: int,
) -> str:
    """Convert a given hex string to a "program" (or just a random, useless string).

    Note:
        This is the slow version of the function that computes big powers.

    Args:
        hex_string: hex string to convert.
        program_length: total number of characters in the program.
        ascii_range: number of distinct ASCII characters in the range.
        ascii_min: minimum ASCII value (inclusive) for readable characters.

    Return:
        Actual ascii characters that may (or may not) be a useful program.
    """
    program_number = int(hex_string, 16)

    program = []
    for position in range(program_length):
        char_index = (program_number // (ascii_range**position)) % ascii_range
        program.append(chr(char_index + ascii_min))

    return "".join(program)


def hex_to_program(
    hex_string: str,
    program_length: int,
    ascii_range: int,
    ascii_min: int,
) -> str:
    """Convert a given hex string to a "program" (or just a random, useless string).

    Args:
        hex_string: hex string to convert.
        program_length: total number of characters in the program.
        ascii_range: number of distinct ASCII characters in the range.
        ascii_min: minimum ASCII value (inclusive) for readable characters.

    Return:
        Actual ascii characters that may (or may not) be a useful program.
    """
    program_number = int(hex_string, 16)

    program = []
    for _ in range(program_length):
        char_index = program_number % ascii_range
        program_number //= ascii_range
        program.append(chr(ascii_min + char_index))

    return "".join(program)


def program_to_hex_slow(
    program: str,
    ascii_min: int,
    ascii_max: int,
    ascii_range: int,
) -> str:
    """Convert the given program string to a hex string.

    Note:
        This is the slow version of the function that computes big powers.

    Args:
        program: ascii string to convert.
        ascii_min: minimum ASCII value (inclusive) for readable characters.
        ascii_max: maximum ASCII value (inclusive) for readable characters.
        ascii_range: number of distinct ASCII characters in the range.

    Return:
        hex string representing the program.
    """
    program_number = 0

    for position, char in enumerate(program):
        ascii_value = ord(char)

        if ascii_value < ascii_min or ascii_value > ascii_max:
            raise ValueError(
                f"Character '{char}' at position {position} is not readable ASCII"
            )

        char_index = ascii_value - ascii_min
        program_number += char_index * ascii_range**position

    return hex(program_number)


def program_to_hex(
    program: str,
    ascii_min: int,
    ascii_range: int,
) -> str:
    """Convert the given program string to a hex string.

    Args:
        program: ascii string to convert.
        ascii_min: minimum ASCII value (inclusive) for readable characters.
        ascii_range: number of distinct ASCII characters in the range.

    Return:
        hex string representing the program.
    """
    program_number = 0

    for char in reversed(program):
        char_index = ord(char) - ascii_min
        program_number = program_number * ascii_range + char_index

    return hex(program_number)


def format_program(
    program: str,
    total_lines: int,
    line_length: int,
) -> str:
    """Add newlines to a given program string.

    Args:
        program: ascii string to format.
        total_lines: total number of lines in the program.
        line_length: number of characters per line.

    Return:
        Nicely formatted string.
    """
    lines = []
    for line_num in range(total_lines):
        start = line_num * line_length
        end = start + line_length
        lines.append(program[start:end])

    return "\n".join(lines)


def random_hex(bytes_needed: int, rng: np.random.Generator) -> str:
    """Return a random hex string usable by hex_to_program."""
    return rng.bytes(bytes_needed).hex()
