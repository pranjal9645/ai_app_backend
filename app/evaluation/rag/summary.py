from dataclasses import dataclass

from app.evaluation.rag.models import RAGEvaluationResult

@dataclass
class RAGContextEvaluationSummary:

    average_context_relevance: float


@dataclass
class RAGEvaluationSummary:
    total_test_cases: int

    total_expected_facts: int
    total_supported_facts: int
    total_unsupported_facts: int

    average_context_relevance: float

    faithful_answers: int
    unfaithful_answers: int

    citation_correct_answers: int
    citation_incorrect_answers: int


def summarize_context_results( results : list[RAGEvaluationResult]) -> RAGContextEvaluationSummary:
    if not results:
        return RAGContextEvaluationSummary(
            average_context_relevance=0.0
        )

    average_relevance = (
        sum(
            result.context_relevance
            for result in results
        )
        / len(results)
    )

    return RAGContextEvaluationSummary(average_context_relevance=average_relevance)


def summarize_results(results : list[RAGEvaluationResult]) -> RAGEvaluationSummary:
    if not results:
         return RAGEvaluationSummary(
            total_test_cases=0,
            total_expected_facts=0,
            total_supported_facts=0,
            total_unsupported_facts=0,
            average_context_relevance=0.0,
            faithful_answers=0,
            unfaithful_answers=0,
            citation_correct_answers=0,
            citation_incorrect_answers=0,
        )
    
    total_expected_facts = sum(
        len(result.expected_facts)
        for result in results
    )

    total_supported_facts = sum(
        len(result.supported_facts)
        for result in results
    )

    total_unsupported_facts = sum(
        len(result.unsupported_facts)
        for result in results
    )

    average_context_relevance = (
        sum(
            result.context_relevance
            for result in results
        )
        / len(results)
    )

    faithful_answers = sum(
        result.faithfulness
        for result in results
    )

    citation_correct_answers = sum(
        result.citation_correctness
        for result in results
    )

    return RAGEvaluationSummary(
        total_test_cases=len(results),

        total_expected_facts=total_expected_facts,
        total_supported_facts=total_supported_facts,
        total_unsupported_facts=total_unsupported_facts,

        average_context_relevance=average_context_relevance,

        faithful_answers=faithful_answers,
        unfaithful_answers=(
            len(results) - faithful_answers
        ),
        citation_correct_answers=citation_correct_answers,
        citation_incorrect_answers=(
            len(results) - citation_correct_answers
        )
    )