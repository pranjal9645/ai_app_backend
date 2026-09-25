
def recall_at_k(expected_chunk_ids : set[int] , retrieved_chunk_ids : list[int] , k : int) -> float:

    if not expected_chunk_ids:
        return 0.0

    top_k = retrieved_chunk_ids[:k]

    retrieved_relevant = (

        set(top_k) & expected_chunk_ids
     )

    return len(retrieved_relevant) / len(expected_chunk_ids)

def precision_at_k(expected_chunk_ids : set[int] , retrieved_chunk_ids : list[int] , k : int ) -> float:
    top_k = retrieved_chunk_ids[:k]

    if not top_k:
        return 0.0

    retrieved_relevant = (
          set(top_k) & expected_chunk_ids
      )

    return len(retrieved_relevant) / len(top_k)


def reciprocal_rank(  expected_chunk_ids: set[int] , retrieved_chunk_ids: list[int]) -> float:

    for rank , chunk_id in enumerate(retrieved_chunk_ids , start=1):

        if chunk_id in expected_chunk_ids:
            return 1.0 / rank


    return 0.0

def mean_reciprocal_rank(results : list[float]) -> float:

    if not results:
        return 0.0

    return sum(results) / len(results)

def summarize_results(results) -> tuple[float , float , float]:

    if not results:
        return 0.0,0.0,0.0

    average_recall = (
        sum(result.recall_at_k for result in results) / len(results)
    )

    average_precision = (
        sum(result.precision_at_k for result in results)
        / len(results)
    )

    mrr = mean_reciprocal_rank(
        [
            result.reciprocal_rank
            for result in results
        ]
    )

    return (
        average_recall , average_precision , mrr
    )