from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models import TransactionType, UUID_LENGTH


class UserIn(BaseModel):
    name: str


class User(BaseModel):
    id: int
    name: str
    balance: Decimal = Field(decimal_places=2)

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: f'{v:.2f}',
        }


class UserBalance(BaseModel):
    id: int
    balance: float

    class Config:
        orm_mode = True


class Transaction(BaseModel):
    uid: str = Field(max_length=UUID_LENGTH)
    type: TransactionType
    amount: Decimal = Field(decimal_places=2)
    timestamp: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: f'{v:.2f}',
        }


class GetBalanceQuery(BaseModel):
    date: datetime
