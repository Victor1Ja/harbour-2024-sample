from fastapi import Depends, HTTPException
from requests import Session
from sqlalchemy import Transaction

from database import get_db
from models import Courier
from schemas import CourierCreate, TransactionBase


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
    db_transaction = Transaction(**transaction.model_dump(), courier_id=courier_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
