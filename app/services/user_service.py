from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User

class UserService:

    def __init__(self , db : Session):
        self.user_repository = UserRepository(db)

    def create_user(self , name : str , email : str):
        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise ValueError("User with this email already exists")

        user = User(name = name , email = email)
        
        return self.user_repository.create(user)
        