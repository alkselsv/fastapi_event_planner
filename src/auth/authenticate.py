from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import JwtTokenHandler

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")


async def authenticate(
    token: str = Depends(oauth2_scheme),
    token_handler: JwtTokenHandler = Depends(JwtTokenHandler)
) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access"
        )
    decoded_token = token_handler.verify_access_token(token)
    return decoded_token["user"]
