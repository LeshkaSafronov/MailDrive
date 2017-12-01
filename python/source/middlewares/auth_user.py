import logging
import random
import base64
import db
import aiopg

from aiohttp.web import middleware, Response
from aiohttp_session import get_session
from settings import CONNECTION_STRING


async def check_basic_auth(request):
    auth_string = request.headers.get('Authorization')
    encoded_string = auth_string.split('Basic ')[1]

    email, password = base64.b64decode(encoded_string).decode().split(':')

    async with aiopg.connect(CONNECTION_STRING) as conn:
        async with conn.cursor() as cursor:
            logging.warning(db.build_universal_select_query(
                'mail_user',
                where={
                    'email': email,
                    'password': password
                }))
            await cursor.execute(db.build_universal_select_query(
                'mail_user',
                where={
                    'email': email,
                    'password': password
                })
            )
            data = await cursor.fetchone()
            if not data:
                return False

    return True


@middleware
async def auth_middleware(request, handler):
    if request.path == '/users/login':
        return await handler(request)

    if 'Authorization' in request.headers:
        if not await check_basic_auth(request):
            return Response(status=401)
        return await handler(request)

    session = await get_session(request)
    if 'authorized' not in session or not session['authorized']:
        return Response(status=401)
    else:
        return await handler(request)
