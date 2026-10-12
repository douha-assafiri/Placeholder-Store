from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from helpers import get_db, get_current_user, create_jwt, hasher, verify_password, get_jwt_expiry, clean_invalid_jwts, \
    logger
from models import User, Roles, InvalidJWTs, Order
from schemas import CreateAccount, AccountResponse, LoginRequest, LoginResponse, PasswordUpdate, OrderResponse

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


@router.post("/create")
async def create_account(account: CreateAccount, db: Session = Depends(get_db)):
    new_user = User(
        name=account.name,
        email=account.email,
        password=hasher.hash(account.password), # Argon2 automatically applies salt,
        dob=account.dob,
        role=Roles.Customer
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    logger.info(f"New user: {new_user.id}")
    return Response(status_code=status.HTTP_201_CREATED, content=f"Account created")


@router.get("/me", response_model=AccountResponse)
async def get_account(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(account: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == account.email).first()
    if user is None or not verify_password(user, account.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_jwt(user.id)
    return LoginResponse(token=token, id=user.id)

@router.delete("/me")
async def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.id} deleted")
    db.delete(current_user)
    db.commit()

@router.post("/logout")
async def logout(authorization: str = Header(...),
                 _user: User = Depends(get_current_user), # get_current_user does check token validity, so nobody submits a bunch of nonsense here.
                 db: Session = Depends(get_db)):
    token = authorization.removeprefix("Bearer ")  # Log out the token from the header, so users can only log themselves out
    db.add(InvalidJWTs(
        jwt=token,
        expiry = get_jwt_expiry(token)
    ))
    db.commit()
    clean_invalid_jwts(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.patch("/me")
async def update_account(new_account_info: CreateAccount, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.name = new_account_info.name
    current_user.email = new_account_info.email
    current_user.dob = new_account_info.dob
    db.commit()
    db.refresh(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch("/me/password")
async def update_password(password: PasswordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if verify_password(current_user, password.old_password):
        current_user.password = hasher.hash(password.new_password)
        logger.info(f"Password updated for user: {current_user.id}")
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials")

@router.get("/me/orders", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
async def view_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.owner == current_user.id).all()