from sqlalchemy.orm import Session

from app.evaluation.retrieval_models import RetrievalEvaluationResult
from app.evaluation.retrieval_dataset import TEST_CASES
from app.repositories.note_repository import NoteRepository
from app.services.embedding_service import EmbeddingService
from app.evaluation.retrieval_metrics import (
    recall_at_k , precision_at_k , reciprocal_rank
)
from app.evaluation.contextual_retrieval.comparison import RetrievalComparisonResult

class RetrievalEvaluator:

    def __init__(self , db : Session , user_id : int):

        self.note_repository = NoteRepository(db)
        self.embedding_service = EmbeddingService()
        self.user_id = user_id


    def evaluate_semantic(self , k : int = 5) -> list[RetrievalEvaluationResult]:

        results = []

        for test_case in TEST_CASES:
            query_embedding = self.embedding_service.create_embedding(test_case.query)

            semantic_results = (
                self.note_repository.semantic_search(user_id=self.user_id , query_embedding=query_embedding , limit=k)
            )

            retrieved_chunk_ids = [
                chunk.id
                for chunk , _distance in semantic_results
            
            ]

            result = RetrievalEvaluationResult(
                query=test_case.query,
                expected_chunk_ids=test_case.relevant_chunk_ids,
                retrieved_chunk_ids=retrieved_chunk_ids,
                recall_at_k=recall_at_k(expected_chunk_ids=test_case.relevant_chunk_ids, retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                precision_at_k=precision_at_k(expected_chunk_ids=test_case.relevant_chunk_ids ,retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                reciprocal_rank=reciprocal_rank(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids)
            )

            results.append(result)


        return results

    def evaluate_lexical(self , k : int = 5) -> list[RetrievalEvaluationResult]:

        results = []

        for test_case in TEST_CASES:

            lexical_results = (
                self.note_repository.full_text_search(user_id=self.user_id , query=test_case.query , limit=k)
            )

            retrieved_chunk_ids = [
            chunk.id
            for chunk, _rank in lexical_results
        ]

            result = RetrievalEvaluationResult(
                 query=test_case.query,
                 expected_chunk_ids=test_case.relevant_chunk_ids,
                 retrieved_chunk_ids=retrieved_chunk_ids,
                 recall_at_k=recall_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                 precision_at_k=precision_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                 reciprocal_rank=reciprocal_rank(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids)
            )

            results.append(result)


        return results

    def evaluate_hybrid(self , k : int = 5) -> list[RetrievalEvaluationResult]:

        results = []

        for test_case in TEST_CASES:

            query_embedding = self.embedding_service.create_embedding(test_case.query)

            semantic_results = self.note_repository.semantic_search(user_id=self.user_id , query_embedding=query_embedding , limit=k)

            lexical_results = self.note_repository.full_text_search(user_id=self.user_id , query=test_case.query , limit=k)

            semantic_chunks = [
                chunk 
                for chunk , _distance in semantic_results
            ]

            lexical_chunks = [
                chunk
                for chunk , _rank in lexical_results
            ]

            semantic_ids = [
                chunk.id 
                for chunk in semantic_chunks
            ]

            lexical_ids = [
                 chunk.id
                 for chunk in lexical_chunks
            ]

            hybrid_chunk_ids = self._fuse_rrf(semantic_ids = semantic_ids , lexical_ids = lexical_ids)

            retrieved_chunk_ids = hybrid_chunk_ids[:k]

            result = RetrievalEvaluationResult(
                query=test_case.query,
                expected_chunk_ids=test_case.relevant_chunk_ids,
                retrieved_chunk_ids=retrieved_chunk_ids,
                recall_at_k=recall_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                precision_at_k=precision_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids , k=k),
                reciprocal_rank=reciprocal_rank(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=retrieved_chunk_ids)
            )

            results.append(result)


        return results


    def _fuse_rrf(self , semantic_ids : list[int] , lexical_ids : list[int]) -> list[int]:
        k = 60

        scores = {}

        for rank , chunk_id in enumerate(semantic_ids , start=1):
            scores[chunk_id] = (
                scores.get(chunk_id , 0.0) + 1.0 / (k + rank)
            )


        for rank , chunk_id in enumerate(lexical_ids , start=1):
            scores[chunk_id] = (
                scores.get(chunk_id , 0.0) + 1.0 / (k + rank)
            )


        return [
            chunk_id

            for chunk_id , _score in sorted(
                scores.items() , key=lambda item : item[1],
                reverse=True
            )
        ]

    def compare_contextual_and_raw_retrieval(self  , k : int = 5) -> list[RetrievalComparisonResult]:

        note_chunks = self.note_repository.get_note_chunks(user_id=self.user_id)
        embeddings = []
        for chunk in note_chunks:
            embedding = self.embedding_service.create_embedding(chunk.content)
            embeddings.append(embedding)

        
        results = []
        for test_case in TEST_CASES:
         query_embedding = self.embedding_service.create_embedding(test_case.query)
         raw_note_chunks = self.note_repository.semantic_search_with_raw_content_embedding(user_id = self.user_id , note_chunks = note_chunks , content_embeddings = embeddings, query_embedding = query_embedding , limit = k)
         contextual_note_chunks = self.note_repository.semantic_search(user_id=self.user_id ,query_embedding= query_embedding , limit=k)

         raw_note_chunk_ids = [
             chunk.id
             for chunk , _distance in raw_note_chunks
         ]

         contextual_note_chunk_ids = [
             chunk.id
             for chunk , _distance in contextual_note_chunks
         ]

         raw_recall_at_k = recall_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=raw_note_chunk_ids , k=k)
         contextual_recall_at_k = recall_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=contextual_note_chunk_ids,k=k)
         raw_precision_at_k = precision_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=raw_note_chunk_ids,k=k)
         contextual_precision_at_k = precision_at_k(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=contextual_note_chunk_ids,k=k)
         raw_reciprocal_rank = reciprocal_rank(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=raw_note_chunk_ids)
         contextual_reciprocal_rank = reciprocal_rank(expected_chunk_ids=test_case.relevant_chunk_ids , retrieved_chunk_ids=contextual_note_chunk_ids)


         result = RetrievalComparisonResult(
             query=test_case.query,
             expected_chunk_ids=test_case.relevant_chunk_ids,
             raw_chunk_ids=raw_note_chunk_ids,
             contextual_chunk_ids=contextual_note_chunk_ids,
             raw_recall_at_k=raw_recall_at_k,
             contextual_recall_at_k=contextual_recall_at_k,
             raw_precision_at_k=raw_precision_at_k,
             contextual_precision_at_k=contextual_precision_at_k,
             raw_reciprocal_rank=raw_reciprocal_rank,
             contextual_reciprocal_rank=contextual_reciprocal_rank
         )

         results.append(result)

        return results
















    
