from aiohttp import web

from app.api.endpoints import UserHandler
from app.api.endpoints import TransactionsHandler


def add_routes(app: web.Application):
    user_handler = UserHandler()
    transaction_handler = TransactionsHandler()

    app.router.add_route(
        'POST', r'/v1/user',
        user_handler.create_user,
        name='create_user'
    )
    app.router.add_route(
        'GET', r'/v1/user/{user_id:\d+}',
        user_handler.get_user_balance,
        name='get_user'
    )
    app.router.add_route(
        'POST', r'/v1/user/{user_id:\d+}/transaction',
        transaction_handler.add_transaction,
        name='add_transaction'
    )
    app.router.add_route(
        'GET', r'/v1/user/{user_id:\d+}/transaction/{transaction_id:[\d\w-]+}',
        transaction_handler.get_transaction,
        name='incoming_transaction'
    )
