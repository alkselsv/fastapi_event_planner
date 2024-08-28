import httpx
import pytest
from auth.jwt_handler import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from models.events import Event
from typing import AsyncGenerator


@pytest.fixture
async def access_token() -> str:
    return create_access_token("testuser@server.com")


@pytest.fixture
async def mock_event(test_session: AsyncSession) -> AsyncGenerator[Event, None]:
    new_event = Event(
        creator="testuser@server.com",
        title="Event title",
        image="https://link-to-image.com/image.png",
        description="Event description",
        tags=["tag1", "tag2"],
        location="Event location",
    )
    test_session.add(new_event)
    await test_session.commit()
    await test_session.refresh(new_event)
    yield new_event
    # await test_session.delete(new_event)
    # await test_session.commit()
    await test_session.rollback()


@pytest.mark.asyncio
async def test_get_events(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/event/", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["title"] == mock_event.title


@pytest.mark.asyncio
async def test_get_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/event/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == mock_event.title


@pytest.mark.asyncio
async def test_post_event(client: httpx.AsyncClient, access_token: str) -> None:
    payload = {
        "title": "Event title",
        "image": "https://link-to-image.com/image.png",
        "description": "Event description",
        "tags": ["tag1", "tag2"],
        "location": "Event location",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    test_response = {"message": "Event created successfully"}
    response = await client.post("/event/new", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response


@pytest.mark.asyncio
async def test_update_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    test_payload = {"title": "Updated event title"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = await client.patch("/event/edit/1", json=test_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_payload["title"]


@pytest.mark.asyncio
async def test_delete_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    test_response = {"message": "Event deleted successfully"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = await client.delete("/event/delete/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response


@pytest.mark.asyncio
async def test_get_event_again(
    client: httpx.AsyncClient, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/event/1", headers=headers)
    assert response.status_code == 404
