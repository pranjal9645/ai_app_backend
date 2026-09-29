from dataclasses import dataclass

from app.evaluation.contextual_retrieval.comparison import (
    RetrievalComparisonResult,
)


@dataclass
class ContextualRetrievalSummary:
    total_test_cases: int

    average_raw_recall_at_k: float
    average_contextual_recall_at_k: float

    average_raw_precision_at_k: float
    average_contextual_precision_at_k: float

    average_raw_reciprocal_rank: float
    average_contextual_reciprocal_rank: float


def summarize_results(
    results: list[RetrievalComparisonResult],
) -> ContextualRetrievalSummary:

    if not results:
        return ContextualRetrievalSummary(
            total_test_cases=0,
            average_raw_recall_at_k=0.0,
            average_contextual_recall_at_k=0.0,
            average_raw_precision_at_k=0.0,
            average_contextual_precision_at_k=0.0,
            average_raw_reciprocal_rank=0.0,
            average_contextual_reciprocal_rank=0.0,
        )

    count = len(results)

    return ContextualRetrievalSummary(
        total_test_cases=count,

        average_raw_recall_at_k=(
            sum(
                result.raw_recall_at_k
                for result in results
            ) / count
        ),

        average_contextual_recall_at_k=(
            sum(
                result.contextual_recall_at_k
                for result in results
            ) / count
        ),

        average_raw_precision_at_k=(
            sum(
                result.raw_precision_at_k
                for result in results
            ) / count
        ),

        average_contextual_precision_at_k=(
            sum(
                result.contextual_precision_at_k
                for result in results
            ) / count
        ),

        average_raw_reciprocal_rank=(
            sum(
                result.raw_reciprocal_rank
                for result in results
            ) / count
        ),

        average_contextual_reciprocal_rank=(
            sum(
                result.contextual_reciprocal_rank
                for result in results
            ) / count
        ),
    )