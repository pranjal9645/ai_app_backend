from datetime import datetime
from sqlalchemy import select , update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken

class RefreshTokenRepository:

    def __init__(self , db : Session):
        self.db = db


    def create(self , refresh_token : RefreshToken) -> RefreshToken:

        self.db.add(refresh_token)
        self.db.flush()

        return refresh_token

    def get_by_token_hash(self , token_hash : str) -> RefreshToken | None:
        statement = (
             select(RefreshToken)
             .where(RefreshToken.token_hash == token_hash)
        )

        return self.db.execute(statement).scalar()

    def revoke(self , refresh_token : RefreshToken , revoked_at : datetime) -> None:
        refresh_token.revoked_at = revoked_at 
        self.db.flush()

    def revoke_all_active_refresh_tokens_for_user(self , user_id : int , revoked_at : datetime) -> None:

        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None)
            )
            .values(
                revoked_at = revoked_at
            )
        )

        self.db.execute(statement)
        self.db.flush()
        