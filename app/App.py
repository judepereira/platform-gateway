from tornado.web import Application


class App(Application):
    def __init__(self, engine_stub, **kwargs):
        self._router = None
        self.engine = engine_stub
        super(App, self).__init__(**kwargs)

    @property
    def router(self):
        return self._router

    def set_router(self, router):
        self._router = router
