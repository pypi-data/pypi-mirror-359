from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from .models import BenchmarkRunResult


def generate_benchmark_table(
    results: list[BenchmarkRunResult], confidence_level: float
) -> Table:
    table = Table(show_header=True, header_style="cyan", expand=True)
    table.add_column("Benchmark", style="dim", width=30)
    table.add_column(f"Mean @ {confidence_level:.0%} CI", justify="right")
    table.add_column("Std Dev", justify="right")
    table.add_column("Stability", justify="right")
    table.add_column("Runs", justify="right")
    table.add_column("Avg Dur~ (s)", justify="right")

    if not results:
        table.add_row("Waiting for benchmarks to start...", "", "", "", "", "")
        return table

    for result in results:
        benchmark_name = result.benchmark.name
        all_runs = [run for case in result.case_results for run in case.runs]

        pending_runs = [r for r in all_runs if r.result.type == "pending"]
        successful_runs = [r for r in all_runs if r.result.type == "success"]
        failed_runs = [r for r in all_runs if r.result.type == "failure"]

        latest_stats = result.stats

        all_cases_done = all(cr.done for cr in result.case_results)

        def with_spinner(text: str | None) -> str | Spinner | Text:
            if pending_runs and not all_cases_done:
                if text:
                    return Spinner("dots", text=Text(text, style="white"), style="cyan")
                return Spinner("dots", style="cyan")
            return text or "[yellow]N/A[/yellow]"

        mean_display_text = None
        if latest_stats:
            mean_val_text = f"{latest_stats.mean * 100:.2f}%"
            if latest_stats.precision:
                margin_of_error = (
                    latest_stats.precision.high - latest_stats.precision.low
                ) / 2
                margin_of_error_text = f"±{margin_of_error * 100:.2f}%"
                mean_display_text = f"{mean_val_text} ({margin_of_error_text})"
            else:
                mean_display_text = mean_val_text

        std_dev_text = f"{latest_stats.std_dev:.3f}" if latest_stats else None
        stability_text = f"{latest_stats.stability * 100:.2f}%" if latest_stats else None

        mean_score_display = with_spinner(mean_display_text)
        std_dev_display = with_spinner(std_dev_text)
        stability_display = with_spinner(stability_text)

        total_runs_count = len(all_runs)
        runs_display_text = f"{total_runs_count}"
        if failed_runs:
            runs_display_text += f" [red]({len(failed_runs)} failed)[/red]"

        avg_run_duration_display: str | Spinner | Text
        avg_runtime_text = None
        completed_runs = successful_runs + failed_runs
        if completed_runs:
            total_runtime = sum(r.result.runtime for r in completed_runs)
            avg_runtime = total_runtime / len(completed_runs)
            avg_runtime_text = f"{avg_runtime:.2f}"

        avg_run_duration_display = with_spinner(avg_runtime_text)

        table.add_row(
            benchmark_name,
            mean_score_display,
            std_dev_display,
            stability_display,
            runs_display_text,
            avg_run_duration_display,
        )

    return table


def generate_failures_table(
    results: list[BenchmarkRunResult]
) -> Table:
    table = Table(show_header=True, header_style="bold red")
    table.title = "Failures"
    table.add_column("Benchmark", style="dim", width=30)
    table.add_column("Case", justify="right")
    table.add_column("Error")
    table.add_column("Stdout")
    table.add_column("Stderr")

    for result in results:
        for case_result in result.case_results:
            for run in case_result.runs:
                if run.result.type == "failure":
                    failure = run.result
                    table.add_row(
                        result.benchmark.name,
                        str(case_result.case.inputs),
                        failure.error_message,
                        failure.stdout.decode("utf-8", errors="ignore"),
                        failure.stderr.decode("utf-8", errors="ignore"),
                    )

    return table
