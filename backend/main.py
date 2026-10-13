from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.events import router as events_router


app = FastAPI(title="Miva Charity & Volunteering Club API")

    
app.include_router(auth_router)
app.include_router(events_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Miva Charity & Volunteering Club API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }