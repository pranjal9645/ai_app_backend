from sqlalchemy.orm import Session
from app.schemas.assistant import (AssistantChatRequest , AssistantChatResponse , AssistantSource)
from app.services.conversation_service import ConversationService

class AssistantService:

    def __init__(self , db : Session):
        self.conversation_service = ConversationService(db=db)


    def chat(self , user_id : int , request : AssistantChatRequest) -> AssistantChatResponse:

        result = self.conversation_service.send_message(user_id=user_id , conversation_id=request.conversation_id , content=request.message)
        rag_result = result.rag_result

        return AssistantChatResponse(
            conversation_id=request.conversation_id,
            message_id=result.message_id,
            answer=rag_result.answer,
            sources=[
                AssistantSource(
                    note_id=source.note_id,
                    chunk_id=source.chunk_id,
                    chunk_index=source.chunk_index,
                    content=source.content
                )
                for source in rag_result.sources
            ]
        )


        