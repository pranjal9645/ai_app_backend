from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:

    def __init__(self , db : Session) :
        self.db = db

    def create(self , token : PasswordResetToken) -> PasswordResetToken:
        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)

        return token

    def get_by_token_hash(self , token_hash : str ) -> PasswordResetToken | None:

        statement = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash == token_hash
            )
        )

        return self.db.scalar(statement)

    def mark_used(self , reset_token : PasswordResetToken , used_at : datetime) -> None:
        reset_token.used_at = used_at
        self.db.flush()