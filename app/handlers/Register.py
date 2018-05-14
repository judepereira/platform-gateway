# -*- coding: utf-8 -*-

from json import loads
from raven.contrib.tornado import SentryMixin
from tornado.web import RequestHandler, HTTPError


class RegisterHandler(SentryMixin, RequestHandler):
    def prepare(self):
        """
        Accept internal metwork only
        """
        # [TODO] only accept from internal network
        if False:
            raise HTTPError(405)

    def post(self):
        """
        Registera a route
        POST -d {method:get, endpoint:/ filename:path.story, linenum:1}
        """
        self.application.register_route(**loads(self.request.body))
        self.set_status(204)

    def delete(self):
        """
        Unregister a route
        """
        self.application.unregister_route(**loads(self.request.body))
        self.set_status(204)
