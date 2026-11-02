
from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.news import router as news_router
from routers.events import router as events_router
from routers.executive_sessions import router as executive_sessions_router
from routers.executives import router as executives_router
from routers.gallery import router as gallery_router
from routers.resources import router as resources_router
from routers.site_content import router as site_content_router


app = FastAPI(title="Miva Charity & Volunteering Club API")


# Register API routers.
app.include_router(auth_router)
app.include_router(news_router)
app.include_router(events_router)
app.include_router(executive_sessions_router)
app.include_router(executives_router)
app.include_router(gallery_router)
app.include_router(resources_router)
app.include_router(site_content_router)


# Root endpoint.
@app.get("/")
def root():
    return {
        "message": "Miva Charity & Volunteering Club API"
    }


# Health check endpoint.
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
