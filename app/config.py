import os


LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:8181")
PORT = os.getenv("PORT", "8000")
SERVICE_NAME = os.getenv("SERVICE_NAME", "default")
WEIGHT = os.getenv("WEIGHT", 1)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_URL = os.getenv("DB_URL")
TES_URL = os.getenv("TES_URL", "http://localhost:8181")


def get_env():
    print(
        {
            "LOAD_BALANCER_URL": LOAD_BALANCER_URL,
            "PORT": PORT,
            "SERVICE_NAME": SERVICE_NAME,
            "WEIGHT": WEIGHT,
            "REDIS_HOST": REDIS_HOST,
            "DB_URL": DB_URL,
            "TES_URL": TES_URL,
        }
    )
