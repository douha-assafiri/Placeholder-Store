from datetime import datetime, timedelta, timezone
import argon2
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION
from database import LocalSession
from models import User, Roles


hasher = argon2.PasswordHasher()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# JWT Explained: https://www.geeksforgeeks.org/web-tech/json-web-token-jwt/
def create_jwt(ident: int) -> str:
    payload = {
        "sub": str(ident),  # Subject (so the user(
        "iat": datetime.now(timezone.utc),  # Issuing time
        "exp": datetime.now(timezone.utc) + timedelta(hours=int(JWT_EXPIRATION)),  # Expiry time
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)  # Encoded into base64 hs265


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])  # Decode with JWT, with what it encrypted with
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()  # Look for the subject in the db
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



# For things that require admin access, acts as middleware basically
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Roles.Staff:
        raise HTTPException(status_code=403, detail="You are not an admin :(")
    return current_user