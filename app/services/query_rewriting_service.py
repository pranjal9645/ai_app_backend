from app.schemas.conversation import (
    ConversationContext , ConversationTurn , RewrittenQuery
)
from app.services.llm_service import LLMService


class QueryRewritingService:
    SYSTEM_PROMPT = """
You rewrite conversational user messages into standalone
search queries for a knowledge retrieval system.

Your task is to use the conversation history to understand
the current user message and produce a self-contained query.

Rules:
- Preserve the user's original intent.
- Resolve pronouns and references when the conversation provides
  enough information to do so.
- Include relevant entities or topics from the conversation when
  necessary for the query to be understandable on its own.
- Do not answer the question.
- Do not add information that is not present in the conversation.
- If the current message is already self-contained, preserve its
  meaning without unnecessary rewriting.
- Return only the rewritten query.
""".strip()

    def __init__(self):
        self.llm_service = LLMService()


    def rewrite(self , context : ConversationContext) -> RewrittenQuery:

        history_text = self._format_history(context.history)

        user_prompt = f"""
Conversation history:
{history_text}

Current user message:
{context.current_message}

Rewrite the current user message into a standalone
search query.

Return only the rewritten query.
""".strip()

        response = self.llm_service.generate(system_prompt=self.SYSTEM_PROMPT , user_prompt=user_prompt)

        return RewrittenQuery(query=response)



    def _format_history(self , history : list[ConversationTurn]) -> str:
        if not history :
            return "(No previous conversation.)"

        lines = []

        for turn in history:
            lines.append(
                f"{turn.role.capitalize()} : {turn.content}"
            )

        return "\n".join(lines)
        