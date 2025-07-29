import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager

import fsspec

from .models import (
    BenchmarkCase,
    BenchmarkRunResult,
    BenchmarkStatistics,
    CaseResult,
    FailureResult,
    NamedBenchmark,
    Run,
    RunConfig,
    RunResult,
    SuccessResult,
)
from .stats import aggregate_benchmark_statistics, calculate_run_stats
from .utils import create_sequential_run_directory


def _serialize_run(run: Run) -> dict:
    result_dump = None
    if hasattr(run.result, "model_dump"):
        result_dump = run.result.model_dump()
        if "stdout" in result_dump and isinstance(result_dump["stdout"], bytes):
            result_dump["stdout"] = result_dump["stdout"].decode("utf-8", "ignore")
        if "stderr" in result_dump and isinstance(result_dump["stderr"], bytes):
            result_dump["stderr"] = result_dump["stderr"].decode("utf-8", "ignore")

    return {
        "result": result_dump,
        "stats": run.stats.model_dump() if run.stats else None,
    }


@contextmanager
def create_results_writer(
    results_dir: str,
    config: RunConfig,
) -> Iterator[Callable[[BenchmarkRunResult], None]]:
    fs, path = fsspec.url_to_fs(results_dir)
    run_dir = create_sequential_run_directory(fs=fs, base_path=path)
    written_runs = set()

    with fs.open(f"{run_dir}/config.json", "w") as f:
        json.dump(config.model_dump(), f, indent=4)

    with fs.open(f"{run_dir}/results.jsonl", "w") as f:

        def writer(result: BenchmarkRunResult) -> None:
            benchmark_name = result.benchmark.name
            for case_idx, case_result in enumerate(result.case_results):
                for run_idx, run in enumerate(case_result.runs):
                    run_id = (benchmark_name, case_idx, run_idx)
                    if run.result.type != "pending" and run_id not in written_runs:
                        run_data = _serialize_run(run)
                        output_record = {
                            "benchmark_name": benchmark_name,
                            "case_index": case_idx,
                            "case_inputs": case_result.case.inputs,
                            "run_index": run_idx,
                            **run_data,
                        }
                        f.write(json.dumps(output_record) + "\n")
                        written_runs.add(run_id)

        yield writer


def load_results(run_path: str) -> tuple[list[BenchmarkRunResult], RunConfig]:
    fs, path = fsspec.url_to_fs(run_path)

    with fs.open(f"{path}/config.json", "r") as f:
        config_dict = json.load(f)
    config = RunConfig(**config_dict)

    results_by_benchmark_case: dict[
        tuple[str, int], list[Run]
    ] = {}

    with fs.open(f"{path}/results.jsonl", "r") as f:
        for line in f:
            record = json.loads(line)
            benchmark_name = record["benchmark_name"]
            case_index = record["case_index"]
            case_inputs = record["case_inputs"]
            run_index = record["run_index"]
            run_data = record["result"]
            stats_data = record["stats"]

            run_result: RunResult
            if run_data["type"] == "success":
                run_result = SuccessResult(
                    comparison=run_data["comparison"],
                    stdout=run_data["stdout"].encode("utf-8"),
                    stderr=run_data["stderr"].encode("utf-8"),
                    runtime=run_data["runtime"],
                )
            elif run_data["type"] == "failure":
                run_result = FailureResult(
                    error_message=run_data["error_message"],
                    stdout=run_data["stdout"].encode("utf-8"),
                    stderr=run_data["stderr"].encode("utf-8"),
                    runtime=run_data["runtime"],
                )
            else:
                # This should not happen with current serialization logic
                continue

            run_stats = (
                BenchmarkStatistics(**stats_data) if stats_data else None
            )
            run = Run(result=run_result, stats=run_stats)

            if (benchmark_name, case_index) not in results_by_benchmark_case:
                results_by_benchmark_case[(benchmark_name, case_index)] = []

            # Ensure the list is long enough to insert at run_index
            current_runs = results_by_benchmark_case[(benchmark_name, case_index)]
            while len(current_runs) <= run_index:
                current_runs.append(None) # type: ignore
            current_runs[run_index] = run


    benchmark_results: dict[str, BenchmarkRunResult] = {}

    for (benchmark_name, case_index), runs in results_by_benchmark_case.items():
        # NOTE: We don't have the original Benchmark object, so we create a dummy one
        # This is acceptable as it's only used for display purposes and not execution
        dummy_benchmark_case = BenchmarkCase(inputs=[], expectation=None)

        # Filter out None runs and calculate stats for the case
        successful_runs_in_case = [r.result for r in runs if r and r.result.type == "success"]
        case_stats = calculate_run_stats(successful_runs_in_case, config.confidence_level)

        case_result = CaseResult(case=dummy_benchmark_case, runs=runs, stats=case_stats)

        if benchmark_name not in benchmark_results:
            dummy_named_benchmark = NamedBenchmark(name=benchmark_name, benchmark=None) # type: ignore
            benchmark_results[benchmark_name] = BenchmarkRunResult(
                benchmark=dummy_named_benchmark, case_results=[], stats=None
            )
        benchmark_results[benchmark_name].case_results.append(case_result)

    # Calculate overall benchmark statistics
    for benchmark_run_result in benchmark_results.values():
        all_case_stats = [cr.stats for cr in benchmark_run_result.case_results if cr.stats]
        benchmark_run_result.stats = aggregate_benchmark_statistics(all_case_stats)

    return list(benchmark_results.values()), config
