from dataclasses import dataclass

@dataclass
class RetrievalComparisonResult:
    query: str
    expected_chunk_ids: set[int]

    raw_chunk_ids: list[int]
    contextual_chunk_ids: list[int]

    raw_recall_at_k: float
    contextual_recall_at_k: float

    raw_precision_at_k: float
    contextual_precision_at_k: float

    raw_reciprocal_rank: float
    contextual_reciprocal_rank: float








