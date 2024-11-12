import httpx
import pytest
from auth.jwt_handler import JwtTokenHandler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.events import Event
from typing import AsyncGenerator
from datetime import datetime


@pytest.fixture
async def access_token() -> str:
    return JwtTokenHandler.create_access_token("testuser@server.com")


@pytest.fixture
async def mock_event(test_session: AsyncSession) -> AsyncGenerator[Event, None]:
    new_event = Event(
        creator="testuser@server.com",
        title="Event title",
        date=datetime(2024, 8, 28, 14, 38, 4),
        description="Event description",
        tags=["tag1", "tag2"],
        location="Event location",
    )
    test_session.add(new_event)
    await test_session.commit()
    await test_session.refresh(new_event)
    yield new_event
    await test_session.delete(new_event)
    await test_session.flush([new_event])


async def test_get_events(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/event/", headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1

    event = response_json[0]
    assert event['title'] == mock_event.title
    assert event['date'] == mock_event.date.isoformat()
    assert event['description'] == mock_event.description
    assert event['tags'] == mock_event.tags
    assert event['location'] == mock_event.location


async def test_get_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str
) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(f"/event/{mock_event.id}", headers=headers)
    assert response.status_code == 200

    event = response.json()
    assert event['title'] == mock_event.title
    assert event['date'] == mock_event.date.isoformat()
    assert event['description'] == mock_event.description
    assert event['tags'] == mock_event.tags
    assert event['location'] == mock_event.location


async def test_post_event(client: httpx.AsyncClient, access_token: str, test_session: AsyncSession) -> None:
    payload = {
        "title": "Event title",
        "date": "2024-08-28T14:38:04",
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

    raw_result = await test_session.execute(select(Event))
    events = [i for i in raw_result.scalars()]
    assert len(events) == 1
    event = events[0]

    assert event.title == "Event title"
    assert event.date == datetime(2024, 8, 28, 14, 38, 4)
    assert event.description == "Event description"
    assert event.tags == ["tag1", "tag2"]
    assert event.location == "Event location"


async def test_update_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str, test_session: AsyncSession
) -> None:
    test_payload = {"title": "Updated event title"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = await client.patch(f"/event/edit/{mock_event.id}", json=test_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_payload["title"]

    test_session.refresh(mock_event)
    assert mock_event.title == "Updated event title"


async def test_delete_event(
    client: httpx.AsyncClient, mock_event: Event, access_token: str, test_session: AsyncSession,
) -> None:
    test_response = {"message": "Event deleted successfully"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = await client.delete(f"/event/delete/{mock_event.id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response
    assert (await test_session.execute(select(Event))).all() == []

    
async def test_get_event_again(client: httpx.AsyncClient, access_token: str) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/event/1", headers=headers)
    assert response.status_code == 404