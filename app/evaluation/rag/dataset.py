from dataclasses import dataclass

@dataclass
class RAGTestCase:
    query : str
    expected_facts : list[str]


TEST_CASES = [
    RAGTestCase(
        query="What is pgvector?",
        expected_facts=[
            "pgvector is a PostgreSQL extension",
            "it provides vector data types",
            "it supports vector similarity search",
        ],
    ),
    RAGTestCase(
        query="How are we using Redis for note caching?",
        expected_facts=[
            "Redis is used to cache note lists",
            "PostgreSQL remains the source of truth",
            "the cache uses version-based invalidation",
        ],
    ),
    RAGTestCase(
        query="How does JWT authentication work?",
        expected_facts=[
            "JWT is used for authentication",
            "the authenticated user is obtained from the JWT",
            "note ownership is based on the authenticated user",
        ],
    ),
    RAGTestCase(
        query="Why do we use both semantic and lexical search?",
        expected_facts=[
            "semantic search captures meaning",
            "lexical search captures exact terms",
            "hybrid search combines both retrieval approaches",
        ],
    ),
    RAGTestCase(
        query="How are embeddings generated for note chunks?",
        expected_facts=[
            "note content is divided into chunks",
            "embeddings are generated for the chunks",
            "the project uses Ollama with nomic-embed-text",
        ],
    ),
]