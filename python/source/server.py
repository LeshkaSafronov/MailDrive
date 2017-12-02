import json
from aiohttp import web
import base64
import aiopg
from mixins.users import UserMixinView
from middlewares.auth_user import auth_middleware
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from settings import CONNECTION_STRING

class APIServer(web.Application, UserMixinView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dbpool = None

    def _register_routes(self):
        UserMixinView._register_routes(self)
        self.router.add_get('/api', self.welcome)

    def welcome(self, request):
        return web.Response(text='Welcome!')

    def _get_cookie_storage(self):
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        return EncryptedCookieStorage(secret_key)

    async def startup(self):
        self._dbpool = await aiopg.create_pool(CONNECTION_STRING)
        self._register_routes()

        setup(self, self._get_cookie_storage())
        self.middlewares.append(auth_middleware)

        await super().startup()

server = APIServer()
web.run_app(server, port=8000)
