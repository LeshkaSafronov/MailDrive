import json
from aiohttp import web
from users import UserMixinView


class APIServer(UserMixinView):
    def __init__(self):
        self._app = web.Application()

    def _register_routes(self):
        self._app.router.add_get('/users', self.list_users)
        self._app.router.add_get('/users/{user_id:\d+}', self.retrieve_user)
        self._app.router.add_post('/users', self.create_user)
        self._app.router.add_put('/users/{user_id:\d+}', self.update_user)



    def start(self):
        self._register_routes()
        web.run_app(self._app, port=8000)


server = APIServer()
server.start()
