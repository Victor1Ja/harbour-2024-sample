# Service model
from asyncio import sleep
import asyncio
import random
import socket
from uplink import Body, Consumer, json, post, timeout

from config import LOAD_BALANCER_URL, PORT, SERVICE_NAME, TES_URL, WEIGHT


class Service(Body):
    name: str
    url: str
    weight: int = 1
    inside_url: str = None


def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


this_service = {
    "name": f"service-{PORT}-{SERVICE_NAME}",
    "url": f"http://localhost:{PORT}",
    "inside_url": f"http://{get_ip_address()}:{PORT}",
    "weight": WEIGHT,
}


class LoadBalancer(Consumer):
    @json
    @post("/register_service")
    def register_service(self, service: Service):
        """Register a service"""


def get_load_balancer(base_url=LOAD_BALANCER_URL):
    print("get_load_balancer-Base URL", base_url)
    return LoadBalancer(base_url="http://load_balancer:8000")


# * Transaction External Service


# * TES Pydantic Models and Uplink API
class TESTransaction(Body):
    amount: int
    currency: str
    description: str
    userId: str


# Transaction External Service API with Uplink and 60s timeout
@timeout(5)
class TES(Consumer):
    @json
    @post("/v1/wallet/transaction")
    def create_transaction(self, transaction: TESTransaction):
        """Create a transaction"""


class TESCircuitBreaker(TES):
    def __init__(self, base_url):
        super().__init__(base_url=base_url)
        self.is_open = False

    def sleep_with_jitter(self, sleep_time):
        jitter = random.randint(0, sleep_time) / 10
        sleep(sleep_time + jitter)

    def open_circuit(self, sleep_time=60):
        self.is_open = True
        self.sleep_with_jitter(sleep_time)
        self.is_open = False

    # Post Transaction with retries and exponential backoff with jitter
    def create_transaction(self, transaction: TESTransaction, retries=3):
        if self.is_open:
            return {"message": "Circuit is open"}
        try:
            response = super().create_transaction(transaction)
            if response.status_code != 200:
                return {"message": "Error in transaction"}
            return response
        except Exception as e:
            if retries == 0:
                asyncio.create_task(self.open_circuit())
                return {
                    "message": "Error in transaction and circuit is open for 60s",
                    "error": str(e),
                }

            sleep_time = 2 ** (3 - retries)
            self.sleep_with_jitter(sleep_time)
            return self.create_transaction(transaction, retries - 1)


def get_tes_api():
    return TES(base_url=TES_URL)
