import asyncio
import random
import redis
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import List, Dict, Any
from pydantic import BaseModel
from contextlib import asynccontextmanager
from urllib.parse import urljoin
import os


print(f"REDIS_HOST: {os.getenv('REDIS_HOST', 'localhost')}")
# Connect to Redis
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0
)


# Service model
class Service(BaseModel):
    name: str
    url: str
    weight: int = 1
    inside_url: str = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    return


async def startup_event():
    print("Starting up")
    # Initialize the service list in Redis
    # if not redis_client.exists("services"):
    redis_client.set("services", "[]")
    # Start the health check background task
    asyncio.create_task(health_check())


# App instance
app = FastAPI(lifespan=lifespan)


def get_services() -> List[Dict[str, Any]]:
    services = redis_client.get("services")
    return eval(services) if services else []


def save_services(services: List[Dict[str, Any]]):
    redis_client.set("services", str(services))


@app.post("/register_service", response_model=Service)
async def register_service(service: Service):
    services = get_services()
    print("Registering service")
    is_in = False
    for s in services:
        print(s)
        if s["url"] == service.url:
            s = service
            is_in = True
            break
    if not is_in:
        services.append(service.model_dump())
    save_services(services)
    return service


@app.get("/services", response_model=List[Service])
async def list_services():
    return get_services()


async def health_check():
    while True:
        services = get_services()
        print("Health check")
        for service in services:
            try:
                response = requests.get(f"{service['inside_url']}/health")
                if response.status_code != 200:
                    services.remove(service)
            except requests.exceptions.RequestException:
                services.remove(service)
        save_services(services)
        await asyncio.sleep(60)


@app.middleware("http")
async def load_balancer_middleware(request: Request, call_next):
    if (
        request.url.path == "/services"
        or request.url.path == "/register_service"
        or request.url.path == "/docs"
        or request.url.path == "/openapi.json"
    ):
        print("Skipping load balancer middleware")
        return await call_next(request)

    services = get_services()
    if not services:
        raise HTTPException(status_code=503, detail="No registered services available")

    total_weight = sum(service["weight"] for service in services)
    chosen_service = None
    random_choice = random.uniform(0, total_weight)
    current_weight = 0

    for service in services:
        current_weight += service["weight"]
        if current_weight >= random_choice:
            chosen_service = service
            break

    if chosen_service is None:
        raise HTTPException(status_code=503, detail="Service selection failed")

    url = urljoin(chosen_service["url"], request.url.path)

    return RedirectResponse(url=url, status_code=307)
