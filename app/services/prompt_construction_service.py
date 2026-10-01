from app.schemas.rag import RAGPrompt
from app.schemas.conversation import ConversationTurn

class PromptConstructionService:
    SYSTEM_PROMPT = """ You are an AI assistant for the user's personal knowledge base.

Answer the user's question using only the provided context.

Do not invent or assume information that is not present
in the context.

If the answer cannot be found in the provided context,
clearly say that the information is not available
in the user's notes.""".strip()


    CONVERSATIONAL_SYSTEM_PROMPT = """
You are an AI assistant for the user's personal knowledge base.

Answer the user's question using the provided retrieved context.

Conversation history is provided only to help you understand
references, pronouns, and conversational context.

The conversation history is not an authoritative source of knowledge.

Use the retrieved context as the source of truth for factual answers.

Do not invent or assume information that is not present
in the retrieved context.

If the answer cannot be found in the retrieved context,
clearly say that the information is not available
in the user's notes.

Do not treat previous assistant responses as factual evidence
unless the same information is supported by the retrieved context.
""".strip()

    def build(self , question : str , context : str) -> RAGPrompt:
        user_prompt = f"""
Context:

{context}

Question:

{question}
""".strip()

        return RAGPrompt(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)


    def build_conversational(self , question : str , context : str , conversation_history : list[ConversationTurn]) -> RAGPrompt:
        history = self._format_conversation_history(conversation_history)
        user_prompt = f"""
        Conversation history:
{history}

Retrieved context:
{context}

Current user question:
{question}
""".strip()

        return RAGPrompt(
            system_prompt=self.CONVERSATIONAL_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )



    def _format_conversation_history(self , history : list[ConversationTurn]) -> str:

        if not history:
            return "(No previous conversation.)"


        lines = []

        for turn in history:
            lines.append(
                f"{turn.role.capitalize()}: {turn.content}"
                )

        return "\n".join(lines)