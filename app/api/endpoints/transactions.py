from aiohttp import web
import json
import pydantic

from app.api import schemas
from app.models import Transaction, InsufficientFunds, UserNotFound


class TransactionsHandler:
    
    async def add_transaction(self, request: web.Request):
        user_id = int(request.match_info['user_id'])
        if request.body_exists:
            content = await request.content.read()
            body = json.loads(content)
        else:
            return web.json_response({
                'message': 'Transaction data is required'
            }, status=404)

        try:
            transaction = schemas.Transaction.parse_obj(body)
        except pydantic.error_wrappers.ValidationError as x:
            return web.json_response(text=x.json(), status=400)

        try:
            transaction_orm = await Transaction.create_for_user(
                user_id,
                transaction.uid,
                transaction.amount,
                transaction.type,
                transaction.timestamp,
            )
        except UserNotFound:
            return web.json_response({
                'message': f'User with id = {user_id} not found'
            }, status=404)
        except InsufficientFunds:
            return web.json_response({
                'message': 'Insufficient founds for withdrawal'
            }, status=402)

        return web.json_response(text=schemas.Transaction.from_orm(transaction_orm).json())

    async def get_transaction(self, request: web.Request):
        user_id = int(request.match_info['user_id'])
        transaction_id = request.match_info['transaction_id']
        
        transaction: Transaction = await Transaction.get_by_uid_for_user(transaction_id, user_id)

        if not transaction:
            return web.json_response({
                'message': f'Transaction with id={transaction_id} does not exist'
            }, status=404)

        schema_transaction = schemas.Transaction.from_orm(transaction)
        return web.json_response(text=schema_transaction.json())
