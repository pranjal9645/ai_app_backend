from app.schemas.rag import RetrievedChunk

class ContextAssemblyService:

    def assemble(self , chunks : list[RetrievedChunk]) -> str :
        if not chunks:
            return ""

        context_parts = []

        for chunk in chunks:
            context_parts.append(
                  f"[Source: note_id={chunk.note_id}, "
                  f"chunk_id={chunk.chunk_id}, "
                  f"chunk_index={chunk.chunk_index}]\n"
                  f"{chunk.content}"
            )

        return "\n\n".join(context_parts)