from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import models, database
from api import api_routes


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup():
    # Create database tables if they don't exist
    models.Base.metadata.create_all(bind=database.engine)

app.include_router(api_routes.router)
