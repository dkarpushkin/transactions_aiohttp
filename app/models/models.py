from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional
import uuid
import asyncpg

from sqlalchemy import Enum
from . import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)
    balance = db.Column(db.DECIMAL(precision=21, scale=2), default=0)

    @staticmethod
    async def get_by_id_with_balance(user_id: int, date: Optional[datetime]) -> 'User':
        user = await User.get(user_id)
        if user is None:
            raise UserNotFound()
            
        if date:
            query = db.text(f'''
                SELECT SUM(
                    CASE
                        WHEN t.type = 'deposit' THEN t.amount
                        WHEN t.type = 'withdraw' THEN -t.amount
                    END) AS s
                FROM {Transaction.__tablename__} as t
                WHERE t.user_id = :user_id AND timestamp <= :timestamp;
            ''')
            row = await db.first(query, user_id=user_id, timestamp=date.date)
            
            user.balance = row[0] if row[0] is not None else 0
        
        return user
        
        


class TransactionType(str, enum.Enum):
    deposit = 'DEPOSIT'
    withdraw = 'WITHDRAW'


UUID_LENGTH = len(str(uuid.uuid4()))


class Transaction(db.Model):
    __tablename__ = 'transactions'

    uid = db.Column(db.String(UUID_LENGTH), primary_key=True)
    amount = db.Column(db.DECIMAL(precision=21, scale=2))
    type = db.Column(Enum(TransactionType), nullable=False)
    timestamp = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def get_by_uid_for_user(uid: str, user_id: int) -> 'Transaction':
        return Transaction.query.where(
            Transaction.uid == uid and Transaction.user_id == user_id
        ).gino.first()

    @staticmethod
    async def create_for_user(user_id: int, uid: str, amount: Decimal, type: TransactionType, timestamp: datetime) -> 'Transaction':
        
        transaction = None

        async with db.transaction() as tx:
            user: User = await User.query.where(User.id == user_id).with_for_update().gino.first()
            if not user:
                raise UserNotFound()
            
            if type == TransactionType.withdraw:
                if user.balance - amount < 0:
                    raise InsufficientFunds()
                
                diff = -amount
            elif type == TransactionType.deposit:
                diff = amount
            else:
                tx.raise_rollback()

            await user.update(balance=user.balance + diff).apply()

            try:
                transaction = await Transaction.create(
                    uid = uid,
                    type = type,
                    amount = amount,
                    timestamp = timestamp,
                    user_id = user_id,
                )
            except asyncpg.exceptions.UniqueViolationError:
                tx.raise_rollback()

        if transaction is None:
            transaction = await Transaction.query.where(Transaction.uid == uid).gino.one()
        
        return transaction


class UserNotFound(Exception):
    message = 'User not found'


class InsufficientFunds(Exception):
    message = 'Insufficient funds for withdrawal'
