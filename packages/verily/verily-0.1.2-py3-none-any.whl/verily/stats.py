import numpy as np
from scipy.stats import t

from .models import BenchmarkStatistics, Interval, SuccessResult


def calculate_stability(scores: list[float]) -> float:
    """
    calculates a stability score between 0 and 1 for a sequence of scores.
    a score of 1.0 indicates perfect stability. this is based on a normalized
    split r-hat diagnostic.
    """
    if len(scores) < 4:
        r_hat = 2.0  # NOTE: not enough data to compute, assign high r-hat
    else:
        n = len(scores)
        half_len = n // 2

        # NOTE: split the sequence into two halves
        chain1 = scores[:half_len]
        chain2 = scores[half_len : half_len * 2]  # NOTE: ensure equal length

        # 1. calculate within-chain variance (w)
        var1 = np.var(chain1, ddof=1)
        var2 = np.var(chain2, ddof=1)
        w = 0.5 * (var1 + var2)

        if w == 0:  # NOTE: avoid division by zero if variance is null
            r_hat = 1.0
        else:
            # 2. calculate between-chain variance (b)
            mean1 = np.mean(chain1)
            mean2 = np.mean(chain2)
            mean_total = np.mean(scores[: half_len * 2])
            b = half_len * ((mean1 - mean_total) ** 2 + (mean2 - mean_total) ** 2)

            # 3. estimate the marginal posterior variance (var_hat)
            var_hat = ((half_len - 1) / half_len) * w + (1 / half_len) * b
            r_hat = np.sqrt(var_hat / w)

    # NOTE: ensure r_hat is at least 1.0 to prevent stability > 100%
    return 1.0 / max(1.0, r_hat)

def aggregate_benchmark_statistics(
    stats_list: list[BenchmarkStatistics],
) -> BenchmarkStatistics | None:
    """
    aggregates a list of benchmark statistics into a single representative
    statistic.
    """
    if not stats_list:
        return None

    mean_of_means = float(np.mean([s.mean for s in stats_list]))
    mean_of_std_devs = float(np.mean([s.std_dev for s in stats_list]))
    mean_of_stabilities = float(np.mean([s.stability for s in stats_list]))

    # NOTE: aggregate precision by taking the pessimistic (widest) interval
    precision_intervals = [s.precision for s in stats_list if s.precision]
    if precision_intervals:
        min_low = float(np.min([p.low for p in precision_intervals]))
        max_high = float(np.max([p.high for p in precision_intervals]))
        aggregated_precision = Interval(low=min_low, high=max_high)
    else:
        aggregated_precision = None

    return BenchmarkStatistics(
        mean=mean_of_means,
        std_dev=mean_of_std_devs,
        precision=aggregated_precision,
        stability=mean_of_stabilities,
    )

def calculate_run_stats(
    runs: list[SuccessResult], confidence_level: float
) -> BenchmarkStatistics | None:
    """
    calculates statistics for a series of successful runs.
    """
    if not runs:
        return None

    similarities = [run.comparison.similarity for run in runs]

    mean_similarity = float(np.mean(similarities))
    std_dev_similarity = (
        float(np.std(similarities, ddof=1)) if len(similarities) > 1 else 0.0
    )

    precision = None
    if len(similarities) > 1:
        # NOTE: calculate confidence interval for the mean
        with np.errstate(invalid="ignore"):  # NOTE: avoid warning when sem is 0
            sem = std_dev_similarity / np.sqrt(len(similarities))
            if sem > 0 and np.isfinite(sem):
                t_crit = t.ppf((1 + confidence_level) / 2, len(similarities) - 1)
                margin_of_error = t_crit * sem
                precision = Interval(
                    low=mean_similarity - margin_of_error,
                    high=mean_similarity + margin_of_error,
                )
            elif sem == 0:
                precision = Interval(low=mean_similarity, high=mean_similarity)

    stability = calculate_stability(similarities)

    return BenchmarkStatistics(
        mean=mean_similarity,
        std_dev=std_dev_similarity,
        precision=precision,
        stability=stability,
    )
