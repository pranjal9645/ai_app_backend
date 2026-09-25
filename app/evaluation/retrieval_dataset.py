from dataclasses import dataclass

@dataclass
class RetrievalTestCase:
    query : str
    relevant_chunk_ids : set[int]



TEST_CASES = [
    RetrievalTestCase(
        query="What is pgvector?",
        relevant_chunk_ids={7,6}
    ),
    RetrievalTestCase(
        query="How are we using Redis for note caching?",
        relevant_chunk_ids={8}
    ),
    RetrievalTestCase(
        query="How does JWT authentication work?",
        relevant_chunk_ids={9}
    ),
    RetrievalTestCase(
        query= "Why do we use both semantic and lexical search?",
        relevant_chunk_ids={11}
    ),
    RetrievalTestCase(
        query="How are embeddings generated for note chunks?",
        relevant_chunk_ids={10}
    )
]
