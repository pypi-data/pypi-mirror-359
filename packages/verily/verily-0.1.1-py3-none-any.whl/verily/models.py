from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict


class Comparisonlike(Protocol):
    similarity: float
    actual: Any
    expected: Any


class Comparer(Protocol):
    async def compare(self, item1: Any, item2: Any) -> Comparisonlike: ...


class RunConfigOverride(BaseModel):
    min_runs: int | None = None
    max_runs: int | None = None
    batch_size: int | None = None
    stability_goal: float | None = None


class BenchmarkCase(BaseModel):
    inputs: list[Any]
    expectation: Any
    config: RunConfigOverride | None = None

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


@dataclass
class Benchmark:
    runner: Callable[..., Awaitable[Any]]
    comparer: Comparer
    cases: list[BenchmarkCase]
    config: RunConfigOverride | None = None


class Comparison(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    similarity: float
    actual: Any
    expected: Any


class SuccessfulEvaluation(BaseModel):
    type: Literal["success"] = "success"
    comparison: Comparison


class FailingEvaluation(BaseModel):
    type: Literal["failure"] = "failure"
    error_message: str


EvaluationResult = SuccessfulEvaluation | FailingEvaluation


class SuccessResult(BaseModel):
    type: Literal["success"] = "success"
    comparison: Comparison
    stdout: bytes
    stderr: bytes
    runtime: float


class FailureResult(BaseModel):
    type: Literal["failure"] = "failure"
    error_message: str
    stdout: bytes
    stderr: bytes
    runtime: float


class PendingResult(BaseModel):
    type: Literal["pending"] = "pending"


RunResult = SuccessResult | FailureResult
RunState = RunResult | PendingResult


@dataclass
class Run:
    result: RunState
    stats: "BenchmarkStatistics | None"


@dataclass
class CaseResult:
    case: BenchmarkCase
    runs: list[Run | None]
    stats: "BenchmarkStatistics | None" = None
    done: bool = False


@dataclass(eq=False)
class NamedBenchmark:
    name: str
    benchmark: Benchmark


@dataclass
class BenchmarkRunResult:
    benchmark: NamedBenchmark
    case_results: list[CaseResult]
    stats: "BenchmarkStatistics | None" = None


@dataclass
class BenchmarkSession:
    results: list[BenchmarkRunResult]


class Interval(BaseModel):
    low: float
    high: float


class BenchmarkStatistics(BaseModel):
    mean: float
    std_dev: float
    precision: Interval | None
    stability: float


RunCallable = Callable[[], Awaitable[RunResult]]


class RunConfig(BaseModel):
    min_runs: int
    max_runs: int
    batch_size: int
    stability_goal: float
    confidence_level: float
