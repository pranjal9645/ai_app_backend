from dataclasses import dataclass

@dataclass
class RAGEvaluationResult:
    query: str
    expected_facts: list[str]
    supported_facts: list[str]
    unsupported_facts: list[str]
    context_relevance: float
    answer : str
    faithfulness : bool
    citation_correctness: bool


