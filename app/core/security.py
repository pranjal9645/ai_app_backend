from pwdlib import PasswordHash
from datetime import datetime , timedelta , timezone
import jwt
from app.core.config import settings
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.exceptions import AuthenticationError

password_hash = PasswordHash.recommended()

def hash_password(password : str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password : str , hashed_password : str) -> bool:

    return password_hash.verify(plain_password , hashed_password) 

def create_access_token(user_id : int) -> str :

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
          "sub": str(user_id),
           "exp": expire
    }

    return jwt.encode(
        payload,settings.jwt_secret_key,algorithm=settings.jwt_algorithm
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# It tells FastAPI:
#"For protected endpoints, get the bearer token from the Authorization header."

def get_current_user(token : str = Depends(oauth2_scheme) , db : Session = Depends(get_db)) -> User:

    try:
        payload = jwt.decode(token , settings.jwt_secret_key , algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationError("Invalid authentication credentials")

    except (jwt.InvalidTokenError , ValueError) :
        raise AuthenticationError("Invalid authentication credentials")

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(int(user_id))

    if not user :
        raise AuthenticationError("User Not found")

    return user


    