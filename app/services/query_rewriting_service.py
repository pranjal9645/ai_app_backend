from app.schemas.conversation import (
    ConversationContext , ConversationTurn , RewrittenQuery
)
from app.services.llm_service import LLMService


class QueryRewritingService:
    SYSTEM_PROMPT = """
You rewrite a user's current conversational message into a
standalone search query for a knowledge retrieval system.

Your primary goal is to preserve the meaning and intent of the
current user message while using conversation history only when
it is necessary to understand that message.

Rules:

1. The current user message is the primary source of intent.

2. If the current message is already self-contained and
   understandable on its own, return it unchanged or make only
   minimal grammatical changes.

3. Do not inject topics, entities, concepts, terminology, or
   assumptions from previous conversation turns into a
   self-contained current message.

4. Use conversation history only to resolve genuine references,
   pronouns, omitted subjects, or context-dependent phrases.

5. If the current message contains a reference such as
   "it", "they", "that", "this", "its", "the previous one",
   "what about that", or similar wording, use the conversation
   history to resolve the reference when the intended meaning
   can be determined.

6. When resolving a reference, include only the information
   from the conversation that is necessary to make the query
   standalone.

7. Do not broaden, narrow, reinterpret, or redirect the user's
   question based on previous conversation topics.

8. Do not assume that the current question is related to the
   previous topic merely because the topics are related.

9. Preserve the user's terminology whenever possible. Do not
   replace a user's term with a related concept unless the
   conversation clearly requires clarification.

10. Do not answer the user's question.

11. Do not add facts that are not present in the current message
    or conversation history.

12. Return only the final standalone search query.
    Do not return explanations, reasoning, labels, quotations,
    or multiple possible queries.

Examples:

Previous Conversation between Assistant and User is Like:

User: What is pgvector?
Assistant: pgvector is an extension for PostgreSQL that provides
vector storage and similarity search.

and now user's Current message is Like:
What are embeddings?

so Output should be:
What are embeddings?

Conversation:
User: What is pgvector?
Assistant: pgvector is an extension for PostgreSQL that provides
vector storage and similarity search.

Current message:
How does it store vectors?

Output:
How does pgvector store vectors?

Conversation:
User: What is pgvector?
Assistant: pgvector is an extension for PostgreSQL that provides
vector storage and similarity search.

Current message:
What are its advantages?

Output:
What are the advantages of pgvector?

Conversation:
User: Tell me about Redis caching.
Assistant: Redis is used to cache note lists.

Current message:
Why do we use it?

Output:
Why do we use Redis for note caching?

Conversation:
User: Explain JWT authentication.
Assistant: JWT authentication protects authenticated API routes.

Current message:
How does that work?

Output:
How does JWT authentication work?

Conversation:
User: What is pgvector?
Assistant: ...

Current message:
What are embeddings and how are they generated?

Output:
What are embeddings and how are they generated?

Important:
A self-contained question must remain independent from the
previous conversation topic. Conversation history exists to
resolve ambiguity, not to influence an otherwise clear query.
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
        