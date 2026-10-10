from fastapi import APIRouter, Depends, HTTPException
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from helpers import get_db, get_current_user, create_jwt, hasher
from models import User, Roles
from schemas import CreateAccount, AccountResponse, LoginRequest, LoginResponse


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)




@router.post("")
async def create_account(account: CreateAccount, db: Session = Depends(get_db)):
    new_user = User(
        name=account.name,
        email=account.email,
        password=hasher.hash(account.password), # Argon2 automatically applies salt,
        dob=account.dob,
        role=Roles.Customer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    #TODO, return a success or something? We shouldnt need a response model for creating an account, just http 200

@router.get("/{account_id}", response_model=User)
async def get_account(account_id: int, current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(account: LoginRequest, db: Session = Depends(get_db)):
    db_account = db.query(User).filter(User.email == account.email).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Incorrect credentials")
    try:
        hasher.verify(account.password, db_account.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=404, detail="Incorrect credentials")
    token = create_jwt(db_account.id)
    return LoginResponse(token=token, id=db_account.id)

@router.delete("/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    db.refresh(current_user)

@router.post("/logout")
async def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass
    #TODO, logout stuff here, maintain a table of invalid JWTs?