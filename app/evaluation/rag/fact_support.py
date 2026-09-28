from app.services.llm_service import LLMService

class FactSupportJudge:

    SYSTEM_PROMPT = """
You are an evaluation system for a Retrieval-Augmented Generation (RAG) application.

Your task is to determine whether an expected fact is supported by the provided context.

A fact is SUPPORTED only if the context contains enough information
to reasonably conclude that the fact is true.

A fact is NOT_SUPPORTED if:
- the context does not contain enough evidence,
- the context contradicts the fact,
- or the fact requires information that is not present in the context.

Use ONLY the provided context.

Do not use outside knowledge.
Do not infer missing information.

you must Respond with exactly one of these two values:

SUPPORTED
NOT_SUPPORTED
""".strip()

    def __init__(self):
        self.llm_service = LLMService()


    def is_supported(self , fact : str , context : str) -> bool:

        user_prompt = f"""
Expected fact:
{fact}

Context:
{context}

Determine whether the expected fact is supported by the context.

you must Respond with exactly:
SUPPORTED

or:

NOT_SUPPORTED
""".strip()

        response = self.llm_service.generate(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)

        normalized_response = response.strip().upper()

        if normalized_response == "SUPPORTED":
            return True

        if normalized_response == "NOT_SUPPORTED":
            return False

        raise ValueError( f"Unexpected fact support judge response: {response}")

