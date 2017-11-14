import logging
import random
from aiohttp.web import middleware
from aiohttp_session import get_session


@middleware
async def auth_middleware(request, handler):
    session = await get_session(request)
    if 'alexey' not in session:
        session['alexey'] = random.randint(1, 10)
    logging.warning('session --> {}'.format(session))
    logging.warning('alexey --> {}'.format(session['alexey']))
    logging.warning('request --> {}'.format(request))
    logging.warning('handler --> {}'.format(handler))
    resp = await handler(request)
    return resp