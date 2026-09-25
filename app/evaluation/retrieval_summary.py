from dataclasses import dataclass

@dataclass
class RetrievalEvaluationSummary:
    recall_at_k: float
    precision_at_k: float
    mean_reciprocal_rank: float