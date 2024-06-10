from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel
# TODO separate stuff into different files


#* Database Connection

load_dotenv()
import os
DB_URL = DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL,echo=True)
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()
        
def init_db():
    Base.metadata.create_all(bind=engine)
    
#* Models
class Courier(Base):
    __tablename__ = "couriers"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255),index=True)
    email = Column(String(255), unique=True, index=True)
    money = Column(Integer,default=0)
    transactions = relationship("Transaction",back_populates="courier")
    is_active = Column(Boolean,default=False)



class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    courier = relationship("Courier",back_populates="transactions")

#* Pydantic Models
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
        
#* Controllers
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

def get_courier(db: Session, courier_id: int):
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if courier is None:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier

def get_couriers(db: Session, skip: int = 0, limit: int = 100):
    print("Getting couriers", skip, limit)
    return db.query(Courier).offset(skip).limit(limit).all()

def create_courier(db: Session, courier: CourierCreate):
    db_courier = Courier(name=courier.name,email=courier.email)
    db.add(db_courier)
    db.commit()
    db.refresh(db_courier)
    return db_courier


def get_transactions(courier_id: int, db:Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.courier_id == courier_id).all()

def create_transaction(transaction: TransactionBase, courier_id: int, db:Session = Depends(get_db)):
    db_transaction = Transaction(**transaction.dict(),courier_id=courier_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

#* FastAPI App

app = FastAPI()
init_db()

#* Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}

@app.post("/store_money")
async def store_money(amount: int, courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
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
async def get_couriers_controller(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print("Getting couriers")
    print(db)
    couriers = get_couriers(db, skip=skip, limit=limit)
    return couriers

@app.get("/couriers/{courier_id}/get_balance")
async def get_balance(courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    return {"balance": courier.money}


#* add Dummy Data
def add_dummy_data(db: Session = Depends(get_db)):
    create_courier(db, CourierCreate(name="John Doe", email="test@test.com"))
    create_courier(db, CourierCreate(name="John Doe1", email="test1@test.com"))
    create_courier(db, CourierCreate(name="John Doe2", email="test2@test.com"))
    create_courier(db, CourierCreate(name="John Doe3", email="test3@test.com"))
    