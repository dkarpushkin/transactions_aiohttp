from aiohttp import web
import json
import pydantic

from app.api import schemas
from app.models import User, UserNotFound


class UserHandler:
    
    async def create_user(self, request: web.Request):
        if request.body_exists:
            content = await request.content.read()
            body = json.loads(content)
        else:
            return web.json_response({
                'message': 'User data is required'
            }, status=404)
        
        try:
            user = schemas.UserIn.parse_obj(body)
        except pydantic.error_wrappers.ValidationError as x:
            return web.json_response(text=x.json(), status=400)

        user_db: User = await User.create(**user.dict())

        schema_user = schemas.User.from_orm(user_db)
        return web.json_response(text=schema_user.json(), status=201)
    
    async def get_user_balance(self, request: web.Request):
        user_id = int(request.match_info['user_id'])
        
        try:
            date = schemas.GetBalanceQuery(**request.query)
        except pydantic.error_wrappers.ValidationError:
            date = None
        
        try:
            user: User = await User.get_by_id_with_balance(user_id, date)
        except UserNotFound:
            return web.json_response({
                'message': f'User with id={user_id} does not exist'
            }, status=404)
        
        schema_user = schemas.User.from_orm(user)

        return web.json_response(text=schema_user.json())
