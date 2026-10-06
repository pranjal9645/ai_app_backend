from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:

    def __init__(self , db : Session):
        self.db = db


    def get_by_email(self , email : str):
        return (
                 self.db.query(User)
                 .filter(User.email == email)
                 .first()
        )

    def create(self , user : User):
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)

        return user

    def get_by_id(self , user_id : int):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_all(self , skip : int = 0 , limit : int = 20):
        return (
            self.db.query(User)
                .order_by(User.id)
                .offset(skip)
                .limit(limit)
                .all()
        )


    def update(self , user : User):
        self.db.flush()
        self.db.refresh(user)

        return user
    def delete(self , user : User):
        self.db.delete(user)
        