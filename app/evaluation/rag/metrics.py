
from app.evaluation.rag.fact_support import FactSupportJudge

def context_relevance(expected_facts : list[str] , supported_facts : list[str]) -> str:

    if not expected_facts:
        return 0.0

    return len(supported_facts) / len(expected_facts)


def find_supported_facts(expected_facts : list[str] , context : str , judge : FactSupportJudge) -> list[str]:
    supported_facts = []


    for fact in expected_facts:

        if judge.is_supported(fact=fact , context=context):
            supported_facts.append(fact)

    return supported_facts

def find_unsupported_facts(expected_facts : list[str] , supported_facts : list[str]) -> list[str]:
    supported_set = set(supported_facts)

    return [
        fact 
        for fact in expected_facts
        if fact not in supported_set
    ]
