from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database.connection import init_db
from routes.events import event_router
from routes.users import user_router

import uvicorn

app = FastAPI()


# Register routes
app.include_router(event_router, prefix="/event")
app.include_router(user_router, prefix="/user")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def home():
    return RedirectResponse(url="/event/")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
