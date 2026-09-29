from app.services.llm_service import LLMService

class ContextualizationService:

    SYSTEM_PROMPT = """
You generate concise contextual information for chunks
of a user's personal knowledge base.

Your task is to explain the context necessary to understand
the provided chunk within the larger document.

Rules:
- Use only information present in the document.
- Do not invent facts.
- Do not rewrite the entire document.
- Keep the contextual description concise.
- Focus on the topic, subject, and relationship of the chunk
  to the document.
- Return only the contextual description.
""".strip()

    def __init__(self):
        self.llm_service = LLMService()
    
    def contextualize(self , note_content : str , chunk_content : str) -> str:

        user_prompt = f"""
Document:
{note_content}

Chunk:
{chunk_content}

Generate a concise contextual description that helps
a semantic search system understand this chunk within
the document.
""".strip()

        context = self.llm_service.generate(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)

        return (
            f"{context.strip()}\n\n"
            f"Chunk:\n"
            f"{chunk_content}"
        )

