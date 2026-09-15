from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.exceptions import (
    UserAlreadyExistsError,UserNotFoundError
)

class UserService:

    def __init__(self , db : Session):
        self.user_repository = UserRepository(db)

    def create_user(self , name : str , email : str):
        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise UserAlreadyExistsError( "User with this email already exists" )

        user = User(name = name , email = email)

        return self.user_repository.create(user)

    def get_user(self , user_id : int):

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError("User not found")

        return user

    def get_users(self):
        return self.user_repository.get_all()

    def update_user(self , user_id : int , name : str , email : str):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError("User not found")
        
        existing_user = self.user_repository.get_by_email(email)

        if existing_user and existing_user.id != user_id:
            raise UserAlreadyExistsError(
            "User with this email already exists"
        )

        user.name = name
        user.email = email

        return self.user_repository.update(user)

    def delete_user(self , user_id : int):

        user = self.user_repository.get_by_id(user_id)
        if not user:
             raise UserNotFoundError("User not found")

        self.user_repository.delete(user)
    
        