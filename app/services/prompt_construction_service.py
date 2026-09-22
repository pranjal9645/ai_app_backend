from app.schemas.rag import RAGPrompt

class PromptConstructionService:
    SYSTEM_PROMPT = """ You are an AI assistant for the user's personal knowledge base.

Answer the user's question using only the provided context.

Do not invent or assume information that is not present
in the context.

If the answer cannot be found in the provided context,
clearly say that the information is not available
in the user's notes.""".strip()

    def build(self , question : str , context : str) -> RAGPrompt:
        user_prompt = f"""
Context:

{context}

Question:

{question}
""".strip()

        return RAGPrompt(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)