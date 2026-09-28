from app.services.llm_service import LLMService

class CitationCorrectnessJudge:
  SYSTEM_PROMPT = """
You are an evaluation system for a Retrieval-Augmented Generation (RAG) application.

Your task is to determine whether the provided sources support
the factual claims made in the generated answer.

A citation is CORRECT if the provided sources contain enough
information to support the claims made in the answer.

A citation is INCORRECT if:
- the sources do not support the answer,
- the sources contradict the answer,
- or the answer contains claims that cannot be supported
  by the provided sources.

Use ONLY the provided sources.

Do not use outside knowledge.
Please you must Respond with exactly one of these two values:
CORRECT
or:
INCORRECT
""".strip()


  def __init__(self):
     self.llm_service = LLMService()

  def is_correct(self , answer : str , sources : str) -> bool:
        user_prompt = f"""
Generated answer:
{answer}

Sources:
{sources}

Determine whether the provided sources support
the factual claims made in the generated answer.

Remember you must Respond with exactly one of these two words:
CORRECT
or:
INCORRECT
""".strip()


        response = self.llm_service.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        normalized_response = response.strip().upper()

        if normalized_response == "CORRECT":
            return True

        if normalized_response == "INCORRECT":
            return False

        raise ValueError(
            f"Unexpected citation correctness response: {response}"
        )
        
     


  
