from dataclasses import dataclass

@dataclass
class RetrievalEvaluationResult:
    query: str
    expected_chunk_ids: set[int]
    retrieved_chunk_ids: list[int]
    recall_at_k: float
    precision_at_k: float
    reciprocal_rank: float

