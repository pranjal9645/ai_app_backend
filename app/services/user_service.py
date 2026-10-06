from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.exceptions import (
    UserAlreadyExistsError,UserNotFoundError
)
from app.core.security import (
    create_access_token , create_refresh_token , get_refresh_token_expiration , hash_refresh_token , hash_password
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from datetime import datetime , timezone
from app.models.refresh_token import RefreshToken

class UserService:

    def __init__(self , db : Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db=db)

    def create_user(self , name : str , email : str , password : str):
        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise UserAlreadyExistsError( "User with this email already exists" )
        
        try:
           hashed_password = hash_password(password)

           user = User(name = name , email = email , password_hash = hashed_password)

           user = self.user_repository.create(user)

           access_token = create_access_token(user_id=user.id)

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
           self.refresh_token_repository.create(refresh_token_object)

           self.db.commit()

           return {
                 "user": user,
                 "access_token": access_token,
                 "refresh_token": refresh_token,
                 "token_type" : "bearer"
           }
        except Exception:
            self.db.rollback()
            raise

    def get_user(self , user_id : int):

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError("User not found")

        return user

    def get_users(self , skip : int = 0 , limit : int = 20):
        return self.user_repository.get_all(skip=skip , limit=limit)

    def update_user(self , user_id : int , name : str , email : str):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError("User not found")
        
        existing_user = self.user_repository.get_by_email(email)

        if existing_user and existing_user.id != user_id:
            raise UserAlreadyExistsError(
            "User with this email already exists"
        )
        try :
          user.name = name
          user.email = email
          updated_user = self.user_repository.update(user)
          self.db.commit()
          return updated_user
        
        except Exception:
            self.db.rollback()
            raise

    def delete_user(self , user_id : int):

        user = self.user_repository.get_by_id(user_id)
        if not user:
             raise UserNotFoundError("User not found")

        self.user_repository.delete(user)
        self.db.commit()
        