# -*- coding: utf-8 -*-

from json import loads
from tornado.web import RequestHandler, HTTPError

from ..utils.Router import make_router


class RegisterHandler(RequestHandler):
    def prepare(self):
        """
        Accept internal metwork only
        """
        # [TODO] only accept from internal network
        if False:
            raise HTTPError(405)

    def post(self):
        """
        Replace all routes
        """
        routes = loads(self.request.body)
        router = make_router(routes)
        self.application.set_router(router)
        self.set_status(204)

    def put(self):
        """
        Add new routes
        """
        pass

    def delete(self):
        """
        Delete a routes
        """
        pass
