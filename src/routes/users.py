from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from database.connection import get_session
from models.users import TokenResponse, SignUpUser, User
from auth.hash_password import HashPassword
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import JwtTokenHandler

user_router = APIRouter(
    tags=["User"],
)


@user_router.post("/signup")
async def sign_user_up(
    data: SignUpUser, session: AsyncSession = Depends(get_session)
) -> dict:
    statement = select(User).where(User.email == data.email)
    result = await session.execute(statement)
    user = result.scalar()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email exists",
        )

    user = User(**data.model_dump())
    hashed_password = HashPassword.create_hash(data.password)
    user.password = hashed_password
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"message": "User successfully registered!"}


@user_router.post("/signin", response_model=TokenResponse)
async def sign_user_in(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> TokenResponse | dict:
    statement = select(User).where(User.email == data.username)
    result = await session.execute(statement)
    user = result.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if not HashPassword.verify_hash(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credential passed"
        )

    access_token = JwtTokenHandler.create_access_token(data.username)
    return TokenResponse(access_token=access_token, token_type="Bearer")
