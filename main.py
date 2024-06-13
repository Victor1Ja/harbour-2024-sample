from asyncio import sleep
import asyncio
import random
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel
from uplink import Consumer, post, json, Body, timeout
import os
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
# TODO separate stuff into different files


# * Database Connection

load_dotenv()

DB_URL = DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


# * Models
class Courier(Base):
    __tablename__ = "couriers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    money = Column(Integer, default=0)
    transactions = relationship("Transaction", back_populates="courier")
    is_active = Column(Boolean, default=False)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    courier = relationship("Courier", back_populates="transactions")


# * Pydantic Models
class CourierBase(BaseModel):
    name: str
    email: str


class CourierCreate(CourierBase):
    pass


class CourierP(CourierBase):
    id: int
    money: int
    is_active: bool

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    amount: int


class TransactionP(TransactionBase):
    id: int
    courier_id: int

    class Config:
        from_attributes = True


# * Uplink API class

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


tes_api = TESCircuitBreaker(base_url="http://localhost:8181")


# * Controllers


def get_courier(db: Session, courier_id: int):
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if courier is None:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier


def get_couriers(db: Session, skip: int = 0, limit: int = 100):
    print("Getting couriers", skip, limit)
    return db.query(Courier).offset(skip).limit(limit).all()


def create_courier(db: Session, courier: CourierCreate):
    db_courier = Courier(name=courier.name, email=courier.email)
    db.add(db_courier)
    db.commit()
    db.refresh(db_courier)
    return db_courier


def get_transactions(courier_id: int, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.courier_id == courier_id).all()


def create_transaction(
    transaction: TransactionBase, courier_id: int, db: Session = Depends(get_db)
):
    db_transaction = Transaction(**transaction.dict(), courier_id=courier_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# * FastAPI App

app = FastAPI()
init_db()


# * Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}


@app.post("/store_money")
async def store_money(amount: int, courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    response_tes = tes_api.create_transaction(
        {
            "amount": amount,
            "currency": "USD",
            "description": "Super White transaction",
            "userId": courier.id,
        }
    )
    if response_tes.status_code != 200:
        return {"message": "Error in transaction"}
    create_transaction(TransactionBase(amount=amount), courier_id, db)
    courier.money += amount
    db.commit()
    return {"message": "Money stored successfully"}


@app.post("/withdraw_money")
async def withdraw_money(amount: int, courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    if courier.money < amount:
        return {"message": "Not enough money"}
    courier.money -= amount
    db.commit()
    return {"message": "Money withdrawn successfully"}


@app.get("/couriers")
async def get_couriers_controller(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    print("Getting couriers")
    print(db)
    couriers = get_couriers(db, skip=skip, limit=limit)
    return couriers


@app.get("/couriers/{courier_id}/get_balance")
async def get_balance(courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    return {"balance": courier.money}


# * add Dummy Data
def add_dummy_data(db: Session = Depends(get_db)):
    create_courier(db, CourierCreate(name="John Doe", email="test@test.com"))
    create_courier(db, CourierCreate(name="John Doe1", email="test1@test.com"))
    create_courier(db, CourierCreate(name="John Doe2", email="test2@test.com"))
    create_courier(db, CourierCreate(name="John Doe3", email="test3@test.com"))
