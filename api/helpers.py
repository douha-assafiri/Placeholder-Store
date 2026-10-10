from datetime import datetime, timedelta, timezone
import argon2
import jwt
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
import time, logging
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION
from database import LocalSession
from models import User, Roles, InvalidJWTs

hasher = argon2.PasswordHasher()
logger = logging.getLogger("api")


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


def is_invalid_jwt(token, db: Session = Depends(get_db)) -> bool:
    if db.query(InvalidJWTs).filter(InvalidJWTs.jwt == token).first() is None:
        return False
    else:
        return True


def get_jwt_expiry(token: str) -> datetime:
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": False},  # Allows us to read expired tokens still
    )
    return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)


def clean_invalid_jwts(db: Session = Depends(get_db)):
    db.query(InvalidJWTs).filter(InvalidJWTs.expiry < datetime.now(timezone.utc)).delete(synchronize_session=False)
    db.commit()


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, JWT_SECRET,
                             algorithms=[JWT_ALGORITHM])  # Decode with JWT, with what it encrypted with
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()  # Look for the subject in the db
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def verify_password(user: User, password: str) -> bool:
    try:
        hasher.verify(user.password, password)
    except VerifyMismatchError:
        return False
    return True


# For things that require admin access, acts as middleware basically
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    logger.debug(f"Admin privileges used by: {current_user.email}")
    if current_user.role != Roles.Staff:
        raise HTTPException(status_code=403, detail="You are not an admin :(")
    return current_user
