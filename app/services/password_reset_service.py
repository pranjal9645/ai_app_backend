from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import (
    create_password_reset_token,
    get_password_reset_token_expiration,
    hash_password,
    hash_password_reset_token,
)
from app.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository
)
from app.repositories.user_repository import UserRepository
from app.models.password_reset_token import PasswordResetToken
from app.core.exceptions import AuthenticationError
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository
)
from app.services.email_service import EmailService

class PasswordResetService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.password_reset_token_repository = PasswordResetTokenRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)
        self.email_service = EmailService()


    def request_password_reset(self, email: str) -> str:
        user = self.user_repository.get_by_email(email=email)

        generic_message = (
            "If an account with that email exists, "
            "a password reset link has been sent."
        )

        if user is None:
            return generic_message

        raw_password_reset_token = create_password_reset_token()
        password_reset_token_hash = hash_password_reset_token(token=raw_password_reset_token)

        expires_at = get_password_reset_token_expiration()

        created_at = datetime.now(timezone.utc)

        try:

            password_reset_token = PasswordResetToken(
                user_id = user.id,
                token_hash=password_reset_token_hash,
                expires_at=expires_at,
                created_at=created_at,
            )
            self.password_reset_token_repository.create(token=password_reset_token)

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        # For a future production-hardening phase, we could introduce an outbox pattern , where email delivery becomes reliably asynchronous.

        self.email_service.send_password_reset_email(recipient_email=user.email , reset_token=raw_password_reset_token)

        return generic_message

    def reset_password(self , token : str, new_password : str) -> None:
        token_hash = hash_password_reset_token(token)

        reset_token = (
            self.password_reset_token_repository
            .get_by_token_hash(token_hash)
        )

        if reset_token is None:
            raise AuthenticationError(
                "Invalid or expired password reset token."
            )
        
        now = datetime.now(timezone.utc)

        if reset_token.used_at is not None:
            raise AuthenticationError(
                "Invalid or expired password reset token."
            )

        if reset_token.expires_at <= now:
            raise AuthenticationError(
                "Invalid or expired password reset token."
            )

        user = self.user_repository.get_by_id(
            reset_token.user_id
        )

        if user is None:
            raise AuthenticationError(
                "Invalid or expired password reset token."
            )

        try:
             user.password_hash = hash_password(new_password)
             self.password_reset_token_repository.mark_used(reset_token=reset_token , used_at=now)
             self.refresh_token_repository.revoke_all_active_refresh_tokens_for_user(user_id=user.id , revoked_at=now)

             self.db.commit()
        except Exception:
            self.db.rollback()
            raise






