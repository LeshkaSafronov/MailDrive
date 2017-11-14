import json
from aiohttp import web
import base64
from mixins.users import UserMixinView
from middlewares.auth_user import auth_middleware
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage


class APIServer(UserMixinView):
    def __init__(self):
        self._app = web.Application()

    def _register_routes(self):
        self._app.router.add_get('/users', self.list_users)
        self._app.router.add_get('/users/{user_id:\d+}', self.retrieve_user)
        self._app.router.add_post('/users', self.create_user)
        self._app.router.add_put('/users/{user_id:\d+}', self.update_user)

    def _get_cookie_storage(self):
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        return EncryptedCookieStorage(secret_key)

    def start(self):
        self._register_routes()
        setup(self._app, self._get_cookie_storage())
        self._app.middlewares.append(auth_middleware)

        web.run_app(self._app, port=8000)


server = APIServer()
server.start()
