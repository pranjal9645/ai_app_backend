from unittest.mock import Mock
import pytest
from app.services.contextualization_service import (
    ContextualizationService,
)


def test_contextualize_generates_context_using_llm():
    service = ContextualizationService()

    service.llm_service = Mock()

    service.llm_service.generate.return_value = (
        "This chunk belongs to the Redis caching architecture."
    )

    note_content = (
        "Our application uses Redis to cache note lists."
    )

    chunk_content = (
        "Redis stores cached note lists."
    )

    result = service.contextualize(
        note_content=note_content,
        chunk_content=chunk_content,
    )

    assert (
        "This chunk belongs to the Redis caching architecture."
        in result
    )

    assert chunk_content in result

    service.llm_service.generate.assert_called_once()

