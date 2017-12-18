import re
import base64
import db
import aiopg
import psycopg2
import psycopg2.extras

from aiohttp.web import middleware, Response
from aiohttp_session import get_session
from settings import CONNECTION_STRING


async def check_basic_auth(request):
    auth_string = request.headers.get('Authorization')
    encoded_string = auth_string.split('Basic ')[1]

    email, password = base64.b64decode(encoded_string).decode().split(':')

    async with aiopg.connect(CONNECTION_STRING) as conn:
        async with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            await cursor.execute(db.build_universal_select_query(
                'maildrive_user',
                where={
                    'email': email,
                    'password': password
                })
            )
            user = await cursor.fetchone()
            if not user:
                return False

            session = await get_session(request)
            session['email'] = user.email
    return True


@middleware
async def auth_middleware(request, handler):
    if re.match('/api/users/(login|singup)', request.path):
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
