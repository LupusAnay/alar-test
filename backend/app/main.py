from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app import views

app = FastAPI()
app.include_router(views.router)
app.mount("/", StaticFiles(directory="../frontend"), name="static")
