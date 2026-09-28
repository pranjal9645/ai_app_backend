from app.evaluation.rag.dataset import RAGTestCase
from app.evaluation.rag.metrics import find_supported_facts , context_relevance , find_unsupported_facts
from sqlalchemy.orm import Session
from app.services.rag_service import RagService
from app.evaluation.rag.dataset import TEST_CASES
from app.evaluation.rag.models import RAGEvaluationResult
from app.evaluation.rag.fact_support import FactSupportJudge
from app.evaluation.rag.faithfulness import FaithfulnessJudge
from app.evaluation.rag.citation import CitationCorrectnessJudge


class RAGEvaluator:

    def __init__(self , db : Session , user_id : int):
        self.rag_service = RagService(db=db)
        self.user_id = user_id
        self.fact_support_judge = FactSupportJudge()
        self.faithfulness_judge = FaithfulnessJudge()
        self.citation_correctness_judge = CitationCorrectnessJudge()
    
        
    def evaluate_context(self , test_case : RAGTestCase) -> RAGEvaluationResult:

        context  = self.rag_service.build_context(user_id=self.user_id , query=test_case.query)

        supported_facts = find_supported_facts(expected_facts=test_case.expected_facts , context=context , judge=self.fact_support_judge)

        unsupported_facts = find_unsupported_facts(expected_facts=test_case.expected_facts , supported_facts=supported_facts)

        relevance = context_relevance(expected_facts=test_case.expected_facts , supported_facts=supported_facts)



        return RAGEvaluationResult(
            query=test_case.query,
            expected_facts=test_case.expected_facts,
            supported_facts=supported_facts,
            unsupported_facts=unsupported_facts,
            context_relevance=relevance
        )

    

    def evaluate_all_contexts(self) -> list[RAGEvaluationResult]:
        results = []

        for test_case in TEST_CASES:
            result = self.evaluate_context(test_case)
            results.append(result)

        return results

    def evaluate_answer(self , test_case : RAGTestCase ) -> RAGEvaluationResult:
        context = self.rag_service.build_context(user_id=self.user_id , query=test_case.query)
        supported_facts = find_supported_facts(expected_facts=test_case.expected_facts , context=context , judge=self.fact_support_judge)
        unsupported_facts = find_unsupported_facts(expected_facts=test_case.expected_facts , supported_facts=supported_facts)
        relevance = context_relevance(expected_facts=test_case.expected_facts , supported_facts=supported_facts)


        answer = self.rag_service.generate_answer_from_context(query=test_case.query , context=context)

        citation_correctness = self.citation_correctness_judge.is_correct(answer=answer , sources=context)

        faithfulness = self.faithfulness_judge.is_faithful(answer=answer , context=context)
        return RAGEvaluationResult(
            query=test_case.query,
            expected_facts=test_case.expected_facts,
            supported_facts=supported_facts,
            unsupported_facts=unsupported_facts,
            context_relevance=relevance,
            answer=answer,
            faithfulness=faithfulness,
            citation_correctness=citation_correctness
        )


    def evaluate_all_answers(self) -> list[RAGEvaluationResult]:
        results = []

        for test_case in TEST_CASES:
            result = self.evaluate_answer(test_case=test_case)
            results.append(result)


        return results
    


    