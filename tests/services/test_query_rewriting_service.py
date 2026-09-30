from unittest.mock import Mock

from app.schemas.conversation import (
    ConversationContext,
    ConversationTurn,
)
from app.services.query_rewriting_service import (
    QueryRewritingService,
)


def test_query_rewriting_uses_conversation_history():

    mock_llm = Mock()

    mock_llm.generate.return_value = (
        "Why did we choose version-based invalidation "
        "for Redis note caching?"
    )

    service = QueryRewritingService()
    service.llm_service = mock_llm

    context = ConversationContext(
        history=[
            ConversationTurn(
                role="user",
                content="How are we using Redis?",
            ),
            ConversationTurn(
                role="assistant",
                content="Redis is used to cache note lists.",
            ),
        ],
        current_message="Why did we choose it?",
    )

    result = service.rewrite(context)

    assert (
        result.query
        == "Why did we choose version-based invalidation "
           "for Redis note caching?"
    )

    mock_llm.generate.assert_called_once()


test_query_rewriting_uses_conversation_history()