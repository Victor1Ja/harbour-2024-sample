from fastapi import FastAPI
from contextlib import asynccontextmanager
import routes

from config import LOAD_BALANCER_URL, get_env
from database import init_db
from api import get_load_balancer, this_service


# * FastAPI App
def register_service():
    load_balancer_api = get_load_balancer(LOAD_BALANCER_URL)
    print("URL", load_balancer_api.session.base_url)
    # res = requests.post("http://load_balancer:8000/register_service", json=this_service)
    res = load_balancer_api.register_service(this_service)
    print(res.content)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_env()
    register_service()
    init_db()
    yield
    return


app = FastAPI(lifespan=lifespan)
app.include_router(routes.router)
