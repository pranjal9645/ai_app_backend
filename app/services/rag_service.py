from app.schemas.rag import RetrievedChunk
from app.services.context_assembly_service import ContextAssemblyService
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.repositories.note_repository import NoteRepository
from app.services.prompt_construction_service import PromptConstructionService
from app.schemas.rag import RAGPrompt , RAGResult
from app.services.llm_service import LLMService
from app.core.config import settings

class RagService:

    def __init__(self , db : Session):
        self.db = db
        self.note_repository = NoteRepository(db)
        self.embedding_service = EmbeddingService()
        self.context_assembly_service = ContextAssemblyService()
        self.prompt_construction_service = PromptConstructionService()
        self.llm_service = LLMService()


    def build_context(self , user_id : int , query : str , top_k : int = 5) -> str:

        chunks = self.retrieve(user_id=user_id , query=query,top_k=top_k)
        chunks = self.filter_relevant_chunks(chunks=chunks)

        if not chunks:
            return "There is no relevant context for this query"
        
        chunks = self.deduplicate_and_order_chunks(chunks=chunks)

        return self.context_assembly_service.assemble(chunks=chunks)

    def retrieve(self , user_id : int , query : str , top_k : int = 5) -> list[RetrievedChunk]:
        query_embedding =  self.embedding_service.create_embedding(query)

        results = self.note_repository.semantic_search(user_id=user_id , query_embedding=query_embedding , limit=top_k)

        chunks = []

        for chunk , distance in results:
            chunks.append(
            RetrievedChunk(
                note_id=chunk.note_id,
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                distance=distance,
                is_anchor=True,
                retrieval_sources=["semantic"]
            )
        )
             
        return chunks

    def expand_with_neighbors(self , user_id : int , chunks : list[RetrievedChunk] , radius : int = 1) -> list[RetrievedChunk]:
        expanded_chunks = []

        for chunk in chunks:
              # Keep the original anchor
            expanded_chunks.append(chunk)

            neighbor_chunks = self.note_repository.get_neighbor_chunks(user_id=user_id , note_id=chunk.note_id,chunk_index=chunk.chunk_index,radius=radius)

            for neighbor in neighbor_chunks:

                  # Skip the anchor itself
                if neighbor.id == chunk.chunk_id:
                      continue
                  
                expanded_chunks.append(
                    RetrievedChunk(
                        note_id=neighbor.note_id,
                        chunk_id=neighbor.id,
                        chunk_index=neighbor.chunk_index,
                        content=neighbor.content,
                        distance=chunk.distance,
                        is_anchor=False,
                        retrieval_sources=["neighbor"]
                    )
                )

        return self.deduplicate_and_order_chunks(chunks=expanded_chunks)
        
        
    def build_prompt(self , user_id : int , query : str , top_k : int = 5) -> RAGPrompt:

        context = self.build_context(user_id=user_id , query=query,top_k=top_k)

        return self.prompt_construction_service.build(question=query , context=context)

    def build_prompt_from_chunks(self , query : str , chunks : list[RetrievedChunk]) -> RAGPrompt:
        context = self.context_assembly_service.assemble(chunks=chunks)
        return self.prompt_construction_service.build(question=query , context=context)
    

    def generate_answer(self , user_id : int , query : str , top_k : int = 5) -> RAGResult:
        chunks = self.hybrid_retrieve(user_id=user_id , query=query , top_k=top_k)
        chunks = self.select_hybrid_results(chunks=chunks)

        if not chunks:
            return RAGResult(
                answer="I couldn't find relevant information in your notes.",
                sources=[]
            )
        
        chunks = self.limit_anchor_diversity(chunks=chunks)

        if not chunks:
            return RAGResult(
        answer="I couldn't find enough relevant information to answer this question.",
        sources=[],
    )
        chunks = self.expand_with_neighbors(user_id=user_id , chunks=chunks)

        chunks = self.apply_context_budget(chunks=chunks)

        if not chunks:
            return RAGResult(
                answer="I couldn't find enough relevant information to answer this question.",
                sources=[]
            )

        

        prompt = self.build_prompt_from_chunks(query=query , chunks=chunks)

        answer = self.llm_service.generate(system_prompt=prompt.system_prompt , user_prompt=prompt.user_prompt)

        return RAGResult(
            answer=answer,
            sources=chunks
        )

    def filter_relevant_chunks(self , chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:
        max_distance = settings.rag_max_distance

        return [
            chunk 
            for chunk in chunks
            if chunk.distance <= max_distance
        ]

    def deduplicate_and_order_chunks(self , chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:
        unique_chunks = {}

        for chunk in chunks:

            existing = unique_chunks.get(chunk.chunk_id)

            if existing is None:
                unique_chunks[chunk.chunk_id] = chunk
                continue

            for source in chunk.retrieval_sources:
                if source not in existing.retrieval_sources:
                    existing.retrieval_sources.append(source)

            if chunk.is_anchor:
                existing.is_anchor = True


            if (existing.distance is None and chunk.distance is not None):
                existing.distance = chunk.distance
                
        return sorted(
            unique_chunks.values(),
            key = lambda chunk : (chunk.note_id , chunk.chunk_index)
        )

    def apply_context_budget(self , chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:
        max_chars = settings.rag_max_context_chars

        anchors = [
            chunk 
            for chunk in chunks
            if chunk.is_anchor
        ]

        neighbors = [
            chunk
            for chunk in chunks
            if not chunk.is_anchor
        ]

        selected_chunks = []
        selected_ids = set()
        total_chars = 0

        # Select semantic anchors first.
        for chunk in anchors:
            chunk_size = len(chunk.content)

            if total_chars + chunk_size > max_chars:
                continue

            selected_chunks.append(chunk)
            selected_ids.add(chunk.chunk_id)
            total_chars += chunk_size

         # Use remaining budget for neighboring chunks.
        for chunk in neighbors:
            
            if chunk.chunk_id in selected_ids:
               continue

            chunk_size = len(chunk.content)

            if total_chars + chunk_size > max_chars:
                  continue
            
            selected_chunks.append(chunk)
            selected_ids.add(chunk.chunk_id)
            total_chars += chunk_size

         # Restore document order for coherent context.

        return sorted(selected_chunks , key=lambda chunk : (chunk.note_id , chunk.chunk_index))

    def limit_anchor_diversity(self , chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:
        max_per_note = settings.rag_max_anchors_per_note

        note_counts = {}
        selected_chunks = []

        for chunk in chunks:
            count = note_counts.get(chunk.note_id , 0)

            if count >= max_per_note:
                continue

            selected_chunks.append(chunk)
            note_counts[chunk.note_id] = count + 1

        return selected_chunks

    def lexical_retrieve(self , user_id : int , query : str , top_k : int = 5) -> list[RetrievedChunk]:
        results = self.note_repository.full_text_search(user_id=user_id , query=query , limit=top_k)

        chunks = []

        for chunk , rank in results:
          chunks.append(
              RetrievedChunk(
                note_id=chunk.note_id,
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                distance=None,
                is_anchor=True,
                retrieval_sources=["lexical"]
              )
          )

        return chunks

    def hybrid_retrieve(self , user_id : int , query : str , top_k : int = 5) -> list[RetrievedChunk]:
        semantic_chunks = self.retrieve(user_id=user_id , query=query , top_k=top_k)

        lexical_chunks = self.lexical_retrieve(user_id=user_id , query=query , top_k=top_k)

        return self.fuse_hybrid_results(semantic_chunks=semantic_chunks , lexical_chunks=lexical_chunks)

    def fuse_hybrid_results(self , semantic_chunks : list[RetrievedChunk] , lexical_chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:
        k = 60

        chunks_by_id = {}

        scores = {}

        for rank , chunk in enumerate(semantic_chunks , start=1):
            chunks_by_id[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = (
                scores.get(chunk.chunk_id,0.0) + 1.0 / (k + rank)
            )

        for rank , chunk in enumerate(lexical_chunks , start=1):
            existing = chunks_by_id.get(chunk.chunk_id)

            if existing is None:
                chunks_by_id[chunk.chunk_id] = chunk
            else:
                for source in chunk.retrieval_sources:
                    if source not in existing.retrieval_sources:
                        existing.retrieval_sources.append(source)

                existing.is_anchor = True

                if(
                    existing.distance is None and chunk.distance is not None
                ):
                    existing.distance = chunk.distance

            scores[chunk.chunk_id] = (
                scores.get(chunk.chunk_id , 0.0) + 1.0 / (k + rank)
            )

        results = []

        for chunk_id , chunk in chunks_by_id.items():
            chunk.hybrid_score = scores[chunk_id]
            results.append(chunk)


        return sorted(results , key=lambda chunk : chunk.hybrid_score or 0.0 , reverse=True)

    def select_hybrid_results(self , chunks : list[RetrievedChunk]) -> list[RetrievedChunk]:

        limit = settings.rag_hybrid_top_k

        return chunks[:limit]


    