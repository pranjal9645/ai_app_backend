from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from sqlalchemy import select , delete
from datetime import datetime , timezone

class ConversationRepository:

    def __init__(self , db : Session):
        self.db = db

    def get_conversation_by_id(self , conversation_id : int , user_id :int) -> Conversation | None:

        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id 
            )
        )

        return self.db.execute(statement).scalar_one_or_none()


    def get_messages(self , conversation_id : int ) -> list[ConversationMessage]:
        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.conversation_id == conversation_id
            )
            .order_by(ConversationMessage.created_at)
        )

        return list(self.db.execute(statement).scalars().all())

    def add_message(self , message : ConversationMessage) -> ConversationMessage:
        self.db.add(message)
        self.db.flush()
        self.db.refresh(message)

        return message


    def touch(self , conversation : Conversation) -> Conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.refresh(conversation)

        return conversation

    def create_conversation(self , conversation : Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        self.db.refresh(conversation)

        return conversation

    def get_all_conversations(self , user_id :int) -> list[Conversation]:

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return list(self.db.execute(statement).scalars().all())


    def delete_conversation(self , conversation : Conversation) -> None:
        self.db.delete(conversation)
        self.db.flush()


    def get_message_by_id(self , messsage_id : int , conversation_id : int) -> ConversationMessage | None:
        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.id == messsage_id ,
                ConversationMessage.conversation_id == conversation_id
            )
        )

        return self.db.execute(statement).scalar_one_or_none()

    def delete_message(self , message : ConversationMessage) -> None:
        self.db.delete(message)
        self.db.flush()


    def get_recent_messages(self , conversation_id : int , limit : int = 10) -> list[ConversationMessage]:
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        )

        messages = list(
            self.db.execute(statement).scalars().all()        
            )

        return list(reversed(messages))


    def search_relevant_messages(self , conversation_id : int , query_embedding : list[float] , limit : int = 5 , excluded_message_ids : set[int | None] = None) -> list[tuple[ConversationMessage , float]]:

        distance = ConversationMessage.embedding.cosine_distance(query_embedding)
        statement = (
            select(ConversationMessage , distance.label("distance"))
            .where(ConversationMessage.conversation_id == conversation_id)
        )

        if excluded_message_ids:
            statement = statement.where(
                ConversationMessage.id.not_in(excluded_message_ids)
            )

        statement = ( statement
                     .order_by(distance)
                     .limit(limit)
                     )

        return list(self.db.execute(statement).all())


    





    


        
