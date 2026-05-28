from fastapi import FastAPI
from app.routers import health, models
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    #this runs before the server starts
    print("Connecting to MongoDB")
    print("Connecting to PLSQL")
    yield
    print("Disconnecting from MongoDB")

app=FastAPI(
    title="XAI LLM Stress Tester",
    description="Explainable AI platform for stress testing fine-tuning",
    version="0.1.0",
    lifespan=lifespan
)
# middleware is like a guard at the entry point of the API.
# here we are allowing the React frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
''' the CORS code given above allows every frontend to access it, 
allows frontend to send sensitive info along with CORS
allowing all REST methods
allows frontend to send extra data desriptions
'''

# attaching all the routes/endpoints from health.py into main app
app.include_router(health.router)
app.include_router(models.router)