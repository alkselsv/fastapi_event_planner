from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from database.connection import get_session
from models.events import EventRequest, EventCreate, EventUpdate, Event
from auth.authenticate import authenticate

event_router = APIRouter(tags=["Events"])


@event_router.get("/", response_model=list[EventRequest])
async def retrieve_all_events(
    user: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
) -> list[Event]:
    statement = select(Event)
    result = await session.execute(statement)
    events = result.scalars().all()
    return list(events)


@event_router.get("/{id}", response_model=EventRequest)
async def retrieve_event(
    id: int,
    user: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
) -> Event:
    event = await session.get(Event, id)
    if event:
        return event
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.post("/new")
async def create_event(
    data: EventCreate,
    user: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
) -> dict:
    event = Event(**data.model_dump())
    event.creator = user
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return {"message": "Event created successfully"}


@event_router.patch("/edit/{id}", response_model=EventRequest)
async def update_event(
    id: int,
    data: EventUpdate,
    user: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
) -> Event | dict:
    event = await session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Operation not allowed"
        )
    event_data = data.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(event, key, value)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@event_router.delete("/delete/{id}")
async def delete_event(
    id: int,
    user: str = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
) -> dict:
    event = await session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Operation not allowed"
        )
    await session.delete(event)
    await session.commit()
    return {"message": "Event deleted successfully"}
