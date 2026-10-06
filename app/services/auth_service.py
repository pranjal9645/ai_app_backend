from sqlalchemy.orm import Session
from app.core.exceptions import AuthenticationError
from datetime import datetime , timezone
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_refresh_token_expiration,
    hash_refresh_token
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.models.refresh_token import RefreshToken

class AuthService:

    def __init__(self , db : Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db=db)


    def login(self , email : str , password : str) :
      
        user = self.user_repository.get_by_email(email)

        if not user:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password , user.password_hash):
            raise AuthenticationError("Invalid email or password")

        try:

          access_token = create_access_token(user_id = user.id)

          refresh_token = create_refresh_token()
          refresh_token_hash = hash_refresh_token(token=refresh_token)

          now = datetime.now(timezone.utc)

          refresh_token_expires_at = get_refresh_token_expiration()

          refresh_token_object = RefreshToken(
            user_id = user.id,
            token_hash = refresh_token_hash,
            expires_at = refresh_token_expires_at,
            created_at = now
          )

          self.refresh_token_repository.create(refresh_token=refresh_token_object)
          self.db.commit()
 
          return {
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "token_type" : "bearer"
         }
        except Exception:
            self.db.rollback()
            raise

    def refresh(self , refresh_token : str):
        token_hash = hash_refresh_token(token=refresh_token)

        stored_token = self.refresh_token_repository.get_by_token_hash(token_hash=token_hash)

        if not stored_token:
            raise AuthenticationError("Invalid refresh token")

        now = datetime.now(timezone.utc)

        if stored_token.revoked_at is not None :

            if stored_token.replaced_by is not None:

                now = datetime.now(timezone.utc)
                self.refresh_token_repository.revoke_all_active_refresh_tokens_for_user(user_id=stored_token.user_id , revoked_at=now)
                self.db.commit()

            raise AuthenticationError("Invalid refresh token")

        if stored_token.expires_at <= now:
            raise AuthenticationError("Refresh token Expired")

        try:
          access_token = create_access_token(user_id=stored_token.user_id)

          new_refresh_token = create_refresh_token()

          new_refresh_token_hash = hash_refresh_token(token=new_refresh_token)

          new_refresh_token_expires_at = get_refresh_token_expiration()

          new_token = RefreshToken(
            user_id = stored_token.user_id,
            token_hash = new_refresh_token_hash,
            expires_at = new_refresh_token_expires_at,
            created_at = now
          )

          self.refresh_token_repository.create(refresh_token=new_token)

          self.refresh_token_repository.revoke(refresh_token=stored_token , revoked_at=now)

          stored_token.replaced_by = new_token.id

          self.db.commit()

          return {
              "access_token": access_token,
              "refresh_token": new_refresh_token,
              "token_type": "bearer"
           }
        except Exception:
            self.db.rollback()
            raise

    def logout(self , refresh_token : str):
        token_hash = hash_refresh_token(refresh_token)

        stored_token = self.refresh_token_repository.get_by_token_hash(token_hash=token_hash)

        if not stored_token:
            raise AuthenticationError("Invalid refresh token")

        if stored_token.revoked_at is not None:
            raise AuthenticationError("Invalid refresh token")

        try:
           now = datetime.now(timezone.utc)

           self.refresh_token_repository.revoke(refresh_token=stored_token , revoked_at=now)

           self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        