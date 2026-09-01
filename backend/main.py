from fastapi import FastAPI

app = FastAPI(title="Miva Charity & Volunteering Club API")


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