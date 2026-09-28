from app.services.llm_service import LLMService

class FaithfulnessJudge:

    SYSTEM_PROMPT = """
You are an evaluation system for a Retrieval-Augmented Generation (RAG) application.

Your task is to determine whether a generated answer is fully supported
by the provided context.

The answer is FAITHFUL only if all factual claims in the answer
are supported by the provided context.

The answer is NOT_FAITHFUL if:
- the answer contains information not supported by the context,
- the answer contradicts the context,
- the answer introduces facts from outside the context,
- or the answer makes an unsupported inference.

Use ONLY the provided context.

Do not use outside knowledge.

you must Respond with exactly one of these two values:

FAITHFUL

or:

NOT_FAITHFUL
""".strip()

    def __init__(self):
        self.llm_service = LLMService()


    def is_faithful(self , answer : str , context : str) -> bool:
           
           user_prompt = f"""
Generated answer:
{answer}

Retrieved context:
{context}

Determine whether the generated answer is fully supported
by the retrieved context.

you must Respond with exactly one of these two words:

FAITHFUL

or:

NOT_FAITHFUL 
""".strip()

           response = self.llm_service.generate(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)

           normalized_response = response.strip().upper()

           if normalized_response == "FAITHFUL":
            return True

           if normalized_response == "NOT_FAITHFUL":
            return False

           raise ValueError(
            f"Unexpected faithfulness judge response: {response}"
        )