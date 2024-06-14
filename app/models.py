from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


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
