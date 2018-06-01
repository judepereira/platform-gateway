# -*- coding: utf-8 -*-

from collections import namedtuple
import os
from pickle import dump, load
from tornado.web import Application

from .utils.Router import make_router


Route = namedtuple('Route', ['endpoint', 'filename', 'block'])


class App(Application):
    def __init__(self, routes_file, **kwargs):

        if os.path.exists(routes_file):
            # Server restarted, load the cache of routes
            with open(routes_file, 'rb') as file:
                self._routes = load(file)
                self._router =  make_router(self._routes)
        else:
            self._routes = {}

            self._router = None

        super(App, self).__init__(routes_file=routes_file, **kwargs)

    @property
    def router(self):
        return self._router

    def register_route(self, method, endpoint, filename, block):
        # add to the already registered routes
        self._routes.setdefault(method, set())\
                    .add(Route(endpoint, filename, block))
        self._rebuild_router()

    def unregister_route(self, method, endpoint, filename, block):
        self._routes.get(method, set())\
                    .remove(Route(endpoint, filename, block))
        self._rebuild_router()

    def _rebuild_router(self):
        # save route to file
        with open(self.settings['routes_file'], 'wb') as file:
            # [TODO] only works for one server
            dump(self._routes, file)

        # rebuild the Router
        self._router = make_router(self._routes)
