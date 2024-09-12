import pytest
import httpx


async def test_sign_new_user(client: httpx.AsyncClient) -> None:

    payload = {
        "email": "testuser@server.com",
        "password": "testpassword",
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    test_response = {"message": "User successfully registered!"}

    response = await client.post("/user/signup", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json() == test_response


async def test_sign_user_in(client: httpx.AsyncClient) -> None:

    payload = {"username": "testuser@server.com", "password": "testpassword"}

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = await client.post("/user/signin", data=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
