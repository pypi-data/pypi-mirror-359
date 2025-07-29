import inspect
import os
import pickle
import time
import traceback
from asyncio import create_subprocess_exec, subprocess
from collections.abc import AsyncIterator, Iterable
from importlib import import_module

from aiostream import stream

from .models import (
    Benchmark,
    BenchmarkCase,
    BenchmarkRunResult,
    BenchmarkSession,
    BenchmarkStatistics,
    CaseResult,
    Comparison,
    EvaluationResult,
    FailingEvaluation,
    FailureResult,
    NamedBenchmark,
    PendingResult,
    Run,
    RunConfig,
    RunConfigOverride,
    RunResult,
    SuccessfulEvaluation,
    SuccessResult,
)
from .stats import aggregate_benchmark_statistics, calculate_run_stats
from .utils import _pipe


class WorkerRuntimeError(RuntimeError):
    def __init__(self, message: str, returncode: int, stdout: bytes, stderr: bytes):
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# TODO: move
def resolve_benchmark(benchmark_path: str) -> Benchmark:
    module_name, instance_name = benchmark_path.split(":")
    module = import_module(module_name)
    benchmark_instance = getattr(module, instance_name)
    if not isinstance(benchmark_instance, Benchmark):
        raise TypeError(
            f"Expected '{instance_name}' in '{module_name}' to be an instance of Benchmark, "
            f"got {type(benchmark_instance).__name__} instead."
        )
    return benchmark_instance


def resolve_benchmarks(benchmark_paths: list[str]) -> Iterable[NamedBenchmark]:
    for path in benchmark_paths:
        if ":" in path:
            yield NamedBenchmark(name=path, benchmark=resolve_benchmark(path))
        else:
            module_name = path.replace("/", ".").removesuffix(".py")
            module = import_module(module_name)
            for name, member in inspect.getmembers(module):
                if isinstance(member, Benchmark):
                    yield NamedBenchmark(
                        name=f"{module_name}:{name}", benchmark=member
                    )


def _get_run_result(read_fd: int) -> EvaluationResult:
    with os.fdopen(read_fd, "rb") as result_pipe_r:
        return pickle.load(result_pipe_r)


def _get_test_name_from_path(benchmark_path: str) -> str:
    try:
        test_name = benchmark_path.split(":")[1]
        return test_name.replace("_", " ").title()
    except IndexError:
        return benchmark_path


def resolve_run_config(
    global_config: RunConfig,
    benchmark_config: RunConfigOverride | None,
    case_config: RunConfigOverride | None,
) -> RunConfig:
    resolved_config = global_config.model_copy()

    if benchmark_config:
        resolved_config.min_runs = benchmark_config.min_runs or resolved_config.min_runs
        resolved_config.max_runs = benchmark_config.max_runs or resolved_config.max_runs
        resolved_config.batch_size = benchmark_config.batch_size or resolved_config.batch_size
        resolved_config.stability_goal = benchmark_config.stability_goal or resolved_config.stability_goal

    if case_config:
        resolved_config.min_runs = case_config.min_runs or resolved_config.min_runs
        resolved_config.max_runs = case_config.max_runs or resolved_config.max_runs
        resolved_config.batch_size = case_config.batch_size or resolved_config.batch_size
        resolved_config.stability_goal = case_config.stability_goal or resolved_config.stability_goal

    return resolved_config


async def run_benchmark_case(
    benchmark: Benchmark,
    case_idx: int,
) -> EvaluationResult:
    case = benchmark.cases[case_idx]

    try:
        result = await benchmark.runner(*case.inputs)
        comparison = Comparison.model_validate(
            await benchmark.comparer.compare(case.expectation, result)
        )
        return SuccessfulEvaluation(comparison=comparison)
    except Exception:
        return FailingEvaluation(error_message=traceback.format_exc())


async def run_single_case(
    benchmark_path_str: str,
    case_idx: int,
) -> RunResult:
    start_time = time.monotonic()

    with _pipe() as (read_fd, write_fd):
        args = [
            "verily",
            "worker",
            "--benchmark-path",
            benchmark_path_str,
            "--case-index",
            str(case_idx),
            "--result-fd",
            str(write_fd),
        ]

        proc = await create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            pass_fds=(write_fd,),
        )

        stdout_bytes, stderr_bytes = await proc.communicate()
        runtime = time.monotonic() - start_time

        if proc.returncode != 0:
            raise WorkerRuntimeError(
                message=f"Worker process exited with code {proc.returncode}.",
                returncode=proc.returncode,
                stdout=stdout_bytes,
                stderr=stderr_bytes,
            )

        try:
            worker_output = _get_run_result(read_fd)
            if not worker_output:
                raise WorkerRuntimeError(
                    message="Worker exited successfully but provided no data via pipe.",
                    returncode=0,
                    stdout=stdout_bytes,
                    stderr=stderr_bytes,
                )
            if worker_output.type == "success":
                return SuccessResult(
                    comparison=worker_output.comparison,
                    stdout=stdout_bytes,
                    stderr=stderr_bytes,
                    runtime=runtime,
                )
            return FailureResult(
                error_message=worker_output.error_message,
                stdout=stdout_bytes,
                stderr=stderr_bytes,
                runtime=runtime,
            )
        except (EOFError, pickle.UnpicklingError) as e:
            raise WorkerRuntimeError(
                message=f"Worker exited successfully but failed to provide valid result via pipe: {type(e).__name__} - {e}",
                returncode=0,
                stdout=stdout_bytes,
                stderr=stderr_bytes,
            )


async def stream_case_runs(
    benchmark_path: str,
    case: BenchmarkCase,
    case_idx: int,
    global_run_config: RunConfig,
    benchmark_run_config_override: RunConfigOverride | None,
) -> AsyncIterator[CaseResult]:

    run_config = resolve_run_config(
        global_config=global_run_config,
        benchmark_config=benchmark_run_config_override,
        case_config=case.config,
    )

    runs: list[Run] = []
    latest_stats: BenchmarkStatistics | None = None
    run_count = 0

    while run_count < run_config.max_runs:
        # if we reach min runs and our latest stats
        # meet the stability goal then we can stop
        if (
            run_count >= run_config.min_runs and
            latest_stats and
            latest_stats.stability >= run_config.stability_goal
        ):
            break

        # Determine batch size for this iteration
        batch_size = min(run_config.batch_size, run_config.max_runs - run_count)
        batch_indices = list(range(run_count, run_count + batch_size))

        run_count += batch_size

        # start with pending results for the new batch
        runs.extend([Run(result=PendingResult(), stats=None) for _ in batch_indices])
        yield CaseResult(case=case, runs=list(runs), stats=latest_stats)

        # note that while this function utlimately only yields once
        # and could just be normal async, we leverage this iterator
        # aspect to ensure we can provide continuos updates via the
        # below stream merge
        async def run_and_update(idx: int) -> AsyncIterator[CaseResult]:
            nonlocal latest_stats
            run_result = await run_single_case(benchmark_path, case_idx)
            runs[idx] = Run(result=run_result, stats=None)
            successful_runs = [
                r.result for r in runs if r and r.result.type == "success"
            ]
            latest_stats = calculate_run_stats(
                successful_runs, run_config.confidence_level
            )
            yield CaseResult(case=case, runs=list(runs), stats=latest_stats)

        batch_runners = [run_and_update(idx) for idx in batch_indices]
        merged_stream = stream.merge(*batch_runners)
        async with merged_stream.stream() as streamer:
            async for case_result in streamer:
                yield case_result

    yield CaseResult(case=case, runs=list(runs), stats=latest_stats, done=True)


async def stream_benchmark_runs(
    benchmark: NamedBenchmark,
    run_config: RunConfig,
) -> AsyncIterator[BenchmarkRunResult]:
    case_results: dict[BenchmarkCase, CaseResult] = {
        case: CaseResult(case=case, runs=[]) for case in benchmark.benchmark.cases
    }

    def get_stats() -> BenchmarkStatistics | None:
        all_stats = [cr.stats for cr in case_results.values() if cr.stats]
        return aggregate_benchmark_statistics(all_stats)

    all_case_runners = [
        stream_case_runs(
            benchmark_path=benchmark.name,
            case=case,
            case_idx=benchmark.benchmark.cases.index(case),
            global_run_config=run_config,
            benchmark_run_config_override=benchmark.benchmark.config,
        )
        for case in benchmark.benchmark.cases
    ]

    merged_stream = stream.merge(*all_case_runners)
    async with merged_stream.stream() as streamer:
        async for case_result in streamer:
            case_results[case_result.case] = case_result
            yield BenchmarkRunResult(
                benchmark=benchmark,
                case_results=list(case_results.values()),
                stats=get_stats(),
            )


# TODO: move or receive the result of resolve_benchmarks instead
async def stream_benchmarks_runs(
    benchmark_paths: list[str],
    run_config: RunConfig,
) -> AsyncIterator[BenchmarkSession]:
    benchmarks = list(resolve_benchmarks(benchmark_paths))
    benchmark_streams = [
        stream_benchmark_runs(
            named_benchmark,
            run_config=run_config,
        )
        for named_benchmark in benchmarks
    ]

    benchmark_states: dict[NamedBenchmark, BenchmarkRunResult] = {}
    merged_stream = stream.merge(*benchmark_streams)
    async with merged_stream.stream() as streamer:
        async for item in streamer:
            benchmark_states[item.benchmark] = item
            yield BenchmarkSession(results=list(benchmark_states.values()))
