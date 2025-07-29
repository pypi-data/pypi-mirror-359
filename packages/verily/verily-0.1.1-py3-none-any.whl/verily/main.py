import asyncio
import os
import pickle
from collections.abc import AsyncIterator
from typing import Annotated

import typer
from rich.console import Console, Group
from rich.live import Live

from .display import (
    generate_benchmark_table,
    generate_failures_table,
)
from .io import create_results_writer, load_results
from .models import BenchmarkSession, RunConfig
from .runner import (
    resolve_benchmark,
    run_benchmark_case,
    stream_benchmarks_runs,
)

app = typer.Typer()


def _render_benchmark_output(
    results: list[BenchmarkSession], config: RunConfig
):
    benchmark_table = generate_benchmark_table(
        results, confidence_level=config.confidence_level
    )

    all_benchmarks_and_cases_done = all(
        all(cr.done for cr in r.case_results) for r in results
    )

    if not all_benchmarks_and_cases_done or not any(
        run.result.type == "failure"
        for r in results
        for case in r.case_results
        for run in case.runs
    ):
        return benchmark_table

    failures_table = generate_failures_table(results)
    return Group(failures_table, benchmark_table)


async def _run_benchmarks(
    stream: AsyncIterator[BenchmarkSession],
    results_dir: str,
    live: Live,
    config: RunConfig,
):
    session: BenchmarkSession | None = None

    live.update(_render_benchmark_output(session.results if session else [], config))

    with create_results_writer(results_dir, config) as write_result:
        async for session in stream:
            live.update(_render_benchmark_output(session.results, config))
            for result in session.results:
                write_result(result)
        live.update(_render_benchmark_output(session.results, config))


async def _run_worker_case_and_dump_result(
    benchmark_path: str,
    case_index: int,
    result_fd: int,
):
    benchmark = resolve_benchmark(benchmark_path)
    output_data = await run_benchmark_case(benchmark, case_index)
    with os.fdopen(result_fd, "wb") as result_pipe_w:
        pickle.dump(output_data, result_pipe_w)


def _show_results(results: list[BenchmarkSession], config: RunConfig, console: Console):
    output = _render_benchmark_output(results, config)
    console.print(output)


@app.command("run")
def run_command(
    benchmark_paths: Annotated[
        list[str],
        typer.Option(
            "--benchmark-path",
            "-b",
            help="Path to the benchmark to run (module:instance or file path)",
        ),
    ],
    min_runs: Annotated[
        int,
        typer.Option(
            "--min-runs",
            help="Minimum number of times to repeat each benchmark case.",
        ),
    ],
    max_runs: Annotated[
        int,
        typer.Option(
            "--max-runs",
            "-r",
            help="Maximum number of times to repeat each benchmark case.",
        ),
    ],
    batch_size: Annotated[
        int,
        typer.Option(
            "--batch-size",
            help="The number of runs to execute in a batch.",
        ),
    ],
    stability_goal: Annotated[
        float,
        typer.Option(
            "--stability-goal",
            help="The stability goal for the benchmark runs.",
        ),
    ],
    confidence_level: Annotated[
        float,
        typer.Option(
            "--confidence-level",
            help="Confidence level for the precision estimate.",
        ),
    ],
    results_dir: Annotated[
        str,
        typer.Option(
            "--results-dir",
            "-o",
            help="Directory to save benchmark results",
        ),
    ],
):
    loop = asyncio.get_event_loop()
    run_config = RunConfig(
        min_runs=min_runs,
        max_runs=max_runs,
        batch_size=batch_size,
        stability_goal=stability_goal,
        confidence_level=confidence_level,
    )
    stream = stream_benchmarks_runs(
        benchmark_paths,
        run_config=run_config,
    )
    with Live(refresh_per_second=10) as live:
        loop.run_until_complete(
            _run_benchmarks(stream, results_dir, live, run_config)
        )


@app.command("worker")
def worker_command(
    benchmark_path: Annotated[
        str,
        typer.Option(
            "--benchmark-path",
            help="Path to the benchmark (module:instance).",
        ),
    ],
    case_index: Annotated[
        int,
        typer.Option(
            "--case-index",
            help="Index of the case to run.",
        ),
    ],
    result_fd: Annotated[
        int,
        typer.Option(
            "--result-fd",
            help="File descriptor to write pickled result to.",
        ),
    ],
):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _run_worker_case_and_dump_result(benchmark_path, case_index, result_fd)
    )


@app.command("show")
def show_command(
    run_path: Annotated[
        str,
        typer.Argument(
            help="Path to the directory containing benchmark results (e.g., a 'run-XXXX' directory)."
        ),
    ],
):
    console = Console()
    results, run_config = load_results(run_path)
    _show_results(results, run_config, console)

