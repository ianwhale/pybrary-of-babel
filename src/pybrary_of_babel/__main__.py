"""CLI for the pybrary application."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict
import shlex

import typer
from loguru import logger

from pybrary_of_babel.experiment import Experiment, ExperimentConfig
from pybrary_of_babel.generate import GeneratorConfig
from pybrary_of_babel.runner import Runner, ExecutionResult


app = typer.Typer(
    add_completion=False,
    help="Run Library-of-Babel-style program-generation experiments.",
)


def _write_results(results: Dict[str, ExecutionResult], output_dir: Path) -> None:
    """Serialize *results* to a JSON-lines file inside *output_dir*."""

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "results.jsonl"

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for hex_key, res in results.items():
            fh.write(
                json.dumps(
                    {
                        "hex": hex_key,
                        "returncode": res.returncode,
                        "stdout": res.stdout.decode(errors="replace"),
                        "stderr": res.stderr.decode(errors="replace"),
                        "ok": res.ok,
                        "timed_out": res.timed_out,
                        "success": res.success,
                    }
                )
                + "\n"
            )

    logger.info(f"Wrote {len(results)} results → {jsonl_path}")


@app.command()
def run(
    n_workers: int = typer.Option(
        ExperimentConfig().n_workers,
        help="Number of workers to use for parallel processing.",
        show_default=True,
    ),
    n_samples: int = typer.Option(
        ExperimentConfig().n_samples,
        help="Total random programs to generate and test.",
        show_default=True,
    ),
    line_length: int = typer.Option(
        GeneratorConfig().line_length,
        help="Characters per line in generated programs.",
        show_default=True,
    ),
    total_lines: int = typer.Option(
        GeneratorConfig().total_lines,
        help="Total lines in generated programs.",
        show_default=True,
    ),
    ascii_min: int = typer.Option(
        GeneratorConfig().ascii_min,
        help="Minimum ASCII value (inclusive) for characters.",
        show_default=True,
    ),
    ascii_max: int = typer.Option(
        GeneratorConfig().ascii_max,
        help="Maximum ASCII value (inclusive) for characters.",
        show_default=True,
    ),
    seed: int | None = typer.Option(
        1234,
        help="Random seed for deterministic program generation.",
        show_default=True,
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=False,
        help="Directory in which to store experiment outputs.",
        show_default=True,
    ),
    versioned: bool = typer.Option(
        True,
        help="Version the *output_dir* with a timestamped subdirectory (default).",
    ),
) -> None:
    """Run an experiment and store its results as JSON lines."""
    if versioned:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        output_dir = output_dir / timestamp

    logger.info(f"Using output directory: {output_dir}")

    experiment_cfg = ExperimentConfig(n_workers=n_workers, n_samples=n_samples)
    generator_cfg = GeneratorConfig(
        line_length=line_length,
        total_lines=total_lines,
        ascii_min=ascii_min,
        ascii_max=ascii_max,
        seed=seed,
    )

    logger.debug(f"ExperimentConfig = {experiment_cfg.model_dump()}")
    logger.debug(f"GeneratorConfig  = {generator_cfg.model_dump()}")

    # Execute experiment
    runner = Runner()
    experiment = Experiment(experiment_cfg, generator_cfg, runner)
    results = experiment.run()

    # Persist results
    _write_results(results, output_dir)

    # Build explicit rerun command including default values
    script_name = "pybrary-of-babel"

    cmd_parts: list[str] = [
        "uv",
        "run",
        script_name,
        "run",
        "--n-workers",
        str(n_workers),
        "--n-samples",
        str(n_samples),
        "--line-length",
        str(line_length),
        "--total-lines",
        str(total_lines),
        "--ascii-min",
        str(ascii_min),
        "--ascii-max",
        str(ascii_max),
        "--output-dir",
        str(output_dir.parent if versioned else output_dir),
    ]

    cmd_parts.append("--versioned" if versioned else "--no-versioned")

    if seed is not None:
        cmd_parts.extend(["--seed", str(seed)])

    rerun_cmd = " ".join(shlex.quote(part) for part in cmd_parts)

    cmd_txt = output_dir / "rerun.txt"
    cmd_txt.write_text(rerun_cmd + "\n", encoding="utf-8")
    logger.info(f"Saved rerun command to {cmd_txt}")


if __name__ == "__main__":
    app()
