from app.core.config import settings
from ollama import Client


EMBEDDING_DIMENSION = 768

class EmbeddingService:

    def __init__(self):
        self.client = Client(host=settings.ollama_host)
        self.model = settings.embedding_model


    def create_embedding(self , text : str) -> list[float]:
        response = self.client.embed(model=self.model , input=text)

        embedding =  response["embeddings"][0]

        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                   f"Invalid embedding dimension: "
                f"expected {EMBEDDING_DIMENSION}, "
                f"got {len(embedding)}"
            )

        return embedding


