from sqlalchemy.orm import Session
from app.models.conversation_message import ConversationMessage
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import (
    ConversationContext,
    ConversationTurn,
)
from app.models.conversation import Conversation
from app.services.rag_service import RagService
from app.schemas.rag import RAGResult
from app.core.exceptions import (
    ConversationNotFoundError , MessageNotFoundError
)
from app.core.config import settings
from app.services.embedding_service import EmbeddingService

class ConversationService:
    def __init__(self , db : Session):
        self.db = db
        self.conversation_repository = ConversationRepository(db=db)
        self.rag_service = RagService(db=db)
        self.embedding_service = EmbeddingService()



    def create_conversation(self , user_id : int , title : str | None = None) -> Conversation:
        try:
            conversation = Conversation(user_id = user_id , title=title)
            conversation = (
                self.conversation_repository.create_conversation(conversation)
            )

            self.db.commit()

            return conversation
        except Exception:
            self.db.rollback()
            raise


    def get_conversations(self , user_id : int) -> list[Conversation]:
        return self.conversation_repository.get_all_conversations(user_id=user_id)


    def delete_conversation(self , user_id : int , conversation_id : int):
        try:
            conversation = self.conversation_repository.get_conversation_by_id(conversation_id=conversation_id , user_id=user_id)

            if conversation is None:
                  raise ConversationNotFoundError(
                    "Conversation not found"
                )

            self.conversation_repository.delete_conversation(conversation=conversation)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise


    def get_messages(self , user_id : int , conversation_id : int) -> list[ConversationMessage]:
        conversation = self.conversation_repository.get_conversation_by_id(conversation_id=conversation_id , user_id=user_id)

        if conversation is None:
             raise ConversationNotFoundError(
                "Conversation not found"
            )

        return self.conversation_repository.get_messages(conversation_id=conversation_id)


    def delete_message(self , user_id : int , conversation_id : int , message_id : int):
        try:
            conversation = self.conversation_repository.get_conversation_by_id(conversation_id=conversation_id , user_id=user_id)

            if conversation is None:
                 raise ConversationNotFoundError(
                    "Conversation not found"
                )

            message = self.conversation_repository.get_message_by_id(messsage_id=message_id , conversation_id=conversation_id)

            if message is None:
               raise MessageNotFoundError(
                    "Message not found"
                )

            self.conversation_repository.delete_message(message=message)

            self.conversation_repository.touch(conversation=conversation)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def send_message(self , user_id : int , conversation_id : int , content : str) -> RAGResult:

        conversation_message_limit = settings.rag_conversation_history_limit
        try:
             conversation = self.conversation_repository.get_conversation_by_id(
                conversation_id=conversation_id,
                user_id=user_id,
            )

             if conversation is None:
                  raise ConversationNotFoundError("Conversation not found")

             messages = self.get_context_messages(
                 user_id=user_id,
                conversation_id=conversation_id,
                current_message=content
            )

             history = [
                ConversationTurn(
                    role=message.role,
                    content=message.content,
                )
                for message in messages
            ]

             conversation_context = ConversationContext(
                history=history,
                current_message=content,
            )

             user_message_embedding = self.embedding_service.create_embedding(text=content)

             user_message = ConversationMessage(
                conversation_id=conversation_id,
                role="user",
                content=content,
                embedding=user_message_embedding
            )

             self.conversation_repository.add_message(user_message)

             result = self.rag_service.generate_conversational_answer(
                user_id=user_id,
                conversation_context=conversation_context
            )

             assistant_message_embedding = self.embedding_service.create_embedding(text=result.answer)

             assistant_message = ConversationMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=result.answer,
                embedding = assistant_message_embedding
             )

             self.conversation_repository.add_message(
                assistant_message
            )

             self.conversation_repository.touch(conversation)

             self.db.commit()

             return result
        except Exception:
            self.db.rollback()
            raise

    def get_context_messages(self , user_id : int , conversation_id : int , current_message : str) -> list[ConversationMessage]:
        conversation_message_limit = settings.rag_conversation_history_limit

        relevant_message_limit =  settings.rag_conversation_relevant_message_limit

        conversation = self.conversation_repository.get_conversation_by_id(conversation_id=conversation_id , user_id=user_id)

        if conversation is None:
            raise ConversationNotFoundError("Conversation Not Found")

        recent_messages = self.conversation_repository.get_recent_messages(conversation_id=conversation_id , limit=conversation_message_limit)

        recent_message_ids = {
            message.id 
            for message in recent_messages
        }

        query_embedding = self.embedding_service.create_embedding(text=current_message)

        relevant_messages = self.conversation_repository.search_relevant_messages(conversation_id=conversation_id , query_embedding=query_embedding , limit=relevant_message_limit , excluded_message_ids=recent_message_ids)

        older_messages = [
            message 
            for message , _distance in relevant_messages
        ]

        all_messages = (recent_messages + older_messages)

        messages_by_id = {
            message.id : message
            for message in all_messages
        }

        return sorted(messages_by_id.values() , key= lambda message : message.created_at)

    def get_conversation(self , conversation_id : int , user_id : int) -> Conversation:

        conversation = self.conversation_repository.get_conversation_by_id(conversation_id=conversation_id , user_id=user_id)

        if conversation is None:
            raise ConversationNotFoundError("Conversation Not Found")

        return conversation
                 
        