from fastapi import APIRouter , Depends , Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate , UserResponse , UserUpdate
from app.schemas.auth import RegisterResponse
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import get_current_user
from app.core.rate_limit import rate_limit


router = APIRouter(prefix="/users" , tags=["Users"])

@router.post("/" , response_model=RegisterResponse , dependencies=[Depends(rate_limit(5,60))])
def create_user(user_data : UserCreate , db : Session = Depends(get_db)):
    service = UserService(db)

    return service.create_user(name=user_data.name , email=user_data.email , password=user_data.password)

@router.get("/me" , response_model=UserResponse)
def get_current_user_profile(current_user : User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}" , response_model=UserResponse)
def get_user(user_id : int , db : Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user(user_id)

@router.get("/" , response_model=list[UserResponse])
def get_users(skip : int = Query(0 , ge=0) ,limit : int = Query(20,ge=1,le=100) , db : Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users(skip=skip , limit=limit)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id : int , user_data : UserUpdate , db : Session = Depends(get_db)):
    service = UserService(db)
    return service.update_user(user_id=user_id , name=user_data.name , email=user_data.email)

@router.delete("/{user_id}")
def delete_user(user_id : int , db : Session = Depends(get_db)):
    service = UserService(db)

    service.delete_user(user_id)

    return {
        "message" : "User deleted Successfully"
    }

