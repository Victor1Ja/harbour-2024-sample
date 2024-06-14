# * Pydantic Models
from pydantic import BaseModel


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
