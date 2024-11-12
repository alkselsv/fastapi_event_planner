from unittest.mock import patch
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User


async def test_sign_new_user(client: httpx.AsyncClient) -> None:

    payload = {
        "email": "testuser@server.com",
        "password": "testpassword",
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    response = await client.post("/user/signup", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered!"}


async def test_sign_user_in(client: httpx.AsyncClient, test_session: AsyncSession) -> None:
    test_session.add(User(
        email="testuser@server.com",
        password="$2b$12$byfLJdZ8Iuo9H.wVUSMdQuq8tsIerzCOkFbplgERURlO7Ngu.VlLO",
    ))

    payload = {"username": "testuser@server.com", "password": "testpassword"}
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    with patch("auth.jwt_handler.JwtTokenHandler.create_access_token", return_value="token"):
        response = await client.post("/user/signin", data=payload, headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "token_type": "Bearer",
            "access_token": "token",
        }
