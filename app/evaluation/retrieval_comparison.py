from app.evaluation.retrieval_evaluator import RetrievalEvaluator
from app.evaluation.retrieval_metrics import summarize_results
from app.evaluation.retrieval_summary import RetrievalEvaluationSummary
from app.evaluation.retrieval_models import RetrievalEvaluationResult

class RetrievalComparison:

    def __init__(self , evaluator : RetrievalEvaluator):
                 self.evaluator = evaluator

    def run(self , k : int = 5) -> dict[str , RetrievalEvaluationResult]:
            semantic_results = (
                    self.evaluator.evaluate_semantic(k=k)
            )

            lexical_results = (
            self.evaluator.evaluate_lexical(k=k)
            )

            hybrid_results = (
            self.evaluator.evaluate_hybrid(k=k)
            )
      

            return{
             "semantic": semantic_results
            ,
            "lexical" : lexical_results ,
            "hybrid": hybrid_results
            }

    def _summarize(self , results : RetrievalEvaluationResult) -> RetrievalEvaluationSummary:
            (
                    recall , precision , mrr
            ) = summarize_results(results)

            return RetrievalEvaluationSummary(
                    recall_at_k=recall , precision_at_k=precision , mean_reciprocal_rank=mrr
            )