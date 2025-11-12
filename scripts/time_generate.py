"""Time the functions in the generate module."""

from timeit import timeit

from pybrary_of_babel.generate import (
    GeneratorConfig,
    program_to_hex,
    program_to_hex_slow,
    hex_to_program,
    hex_to_program_slow,
)


if __name__ == "__main__":
    config = GeneratorConfig()
    # Extract config values to avoid type checker issues with computed fields
    program_length: int = config.program_length  # type: ignore[assignment]
    ascii_range: int = config.ascii_range  # type: ignore[assignment]
    ascii_min: int = config.ascii_min
    ascii_max: int = config.ascii_max

    test_program = " " * program_length

    assert program_to_hex(test_program, ascii_min, ascii_range) == program_to_hex_slow(
        test_program, ascii_min, ascii_max, ascii_range
    )

    test_hex = "0x0e13"
    assert hex_to_program(
        test_hex, program_length, ascii_range, ascii_min
    ) == hex_to_program_slow(test_hex, program_length, ascii_range, ascii_min)

    n_trials = 50

    my_globals = globals()
    print(
        "Average time for program_to_hex: {:0.4f}s".format(
            timeit(
                "program_to_hex(test_program, ascii_min, ascii_range)",
                number=n_trials,
                globals=my_globals,
            )
            / n_trials
        ),
    )
    print(
        "Average time for program_to_hex_slow: {:0.4f}s".format(
            timeit(
                "program_to_hex_slow(test_program, ascii_min, ascii_max, ascii_range)",
                number=n_trials,
                globals=my_globals,
            )
            / n_trials
        ),
    )

    print(
        "Average time for hex_to_program: {:0.4f}s".format(
            timeit(
                "hex_to_program(test_hex, program_length, ascii_range, ascii_min)",
                number=n_trials,
                globals=my_globals,
            )
            / n_trials
        ),
    )
    print(
        "Average time for hex_to_program_slow: {:0.4f}s".format(
            timeit(
                "hex_to_program_slow(test_hex, program_length, ascii_range, ascii_min)",
                number=n_trials,
                globals=my_globals,
            )
            / n_trials
        ),
    )
