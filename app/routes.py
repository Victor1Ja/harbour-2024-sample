# * Routes
from fastapi import APIRouter, Depends
from requests import Session


from api import get_tes_api
from controllers import create_transaction, get_courier, get_couriers
from database import get_db
from schemas import TransactionBase

router = APIRouter()
tes_api = get_tes_api()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}


@router.post("/store_money")
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


@router.post("/withdraw_money")
async def withdraw_money(amount: int, courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    if courier.money < amount:
        return {"message": "Not enough money"}

    response_tes = tes_api.create_transaction(
        {
            "amount": -amount,
            "currency": "USD",
            "description": "Super White transaction",
            "userId": courier.id,
        }
    )
    if response_tes.status_code != 200:
        return {"message": "Error in transaction"}
    create_transaction(TransactionBase(amount=-amount), courier_id, db)
    courier.money -= amount
    db.commit()
    return {"message": "Money withdrawn successfully"}


@router.get("/couriers")
async def get_couriers_controller(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    print("Getting couriers")
    print(db)
    couriers = get_couriers(db, skip=skip, limit=limit)
    return couriers


@router.get("/couriers/{courier_id}/get_balance")
async def get_balance(courier_id: int, db: Session = Depends(get_db)):
    courier = get_courier(db, courier_id)
    return {"balance": courier.money}
