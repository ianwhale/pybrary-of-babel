"""Experiment definition."""

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings
from tqdm import tqdm
from joblib import Parallel, delayed

from pybrary_of_babel.generate import (
    GeneratorConfig,
    hex_to_program,
    random_hex,
)
from pybrary_of_babel.runner import Runner, ExecutionResult


class ExperimentConfig(BaseSettings):
    """Configuration for an experiment."""

    n_workers: int = Field(default=16, description="Number of workers in parallelism.")
    n_samples: int = Field(
        default=100, description="Number of random programs to sample."
    )


class Experiment:
    """Defines an experiment."""

    def __init__(
        self,
        experiment_config: ExperimentConfig,
        generator_config: GeneratorConfig,
        runner: Runner,
    ):
        """Constructor."""

        self.experiment_config = experiment_config
        self.generator_config = generator_config
        self.runner = runner

        self.successful_hex: dict[str, ExecutionResult] = {}

    def run(self) -> dict[str, ExecutionResult]:
        """Run the given experiment."""
        hex_program_map = dict[str, str]()
        print(self.generator_config.program_length)

        n_samples = self.experiment_config.n_samples
        logger.info(f"Generating {n_samples} random programs.")
        with tqdm(total=n_samples) as pbar:
            while len(hex_program_map) < n_samples:
                hex = random_hex(
                    self.generator_config.bytes_needed,  # type: ignore
                    rng=self.generator_config.rng,
                )

                if hex not in hex_program_map:
                    hex_program_map[hex] = hex_to_program(
                        hex,
                        program_length=self.generator_config.program_length,  # type: ignore
                        ascii_range=self.generator_config.ascii_range,  # type: ignore
                        ascii_min=self.generator_config.ascii_min,
                    )
                    pbar.update()

        logger.info("Checking which programs run.")

        def worker(hex: str, program: str) -> tuple[str, ExecutionResult]:
            return hex, self.runner.run(program)

        results = [
            r
            for r in tqdm(
                Parallel(
                    n_jobs=self.experiment_config.n_workers,
                    prefer="threads",
                    require="sharedmem",
                    return_as="generator",
                )(
                    delayed(worker)(hex, program)
                    for hex, program in hex_program_map.items()
                ),
                total=len(hex_program_map),
            )
        ]

        print(self.generator_config.bytes_needed)

        out = {hex: result for hex, result in results if result.success}

        logger.info(f"Got {len(out)} successful program runs.")

        return out


if __name__ == "__main__":
    experiment = Experiment(ExperimentConfig(n_samples=10), GeneratorConfig(), Runner())
    print(experiment.run())
