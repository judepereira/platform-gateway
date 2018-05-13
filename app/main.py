# -*- coding: utf-8 -*-

from tornado import ioloop
from tornado.options import define, options

from .App import App
from .utils.Stub import GrpcStub
from . import handlers


define('debug', default=False, help='enable debug')
define('port', default=8888, help='port to listen on')
define('engine', default='engine:50051', help='engine hostname:port')


def make_app():
    engine_stub = GrpcStub(options.engine)

    _handlers = [
        (r'/\+', handlers.RegisterHandler),
        (r'/(?P<is_file>~/)?(?P<path>.*)', handlers.ExecHandler)
    ]

    return App(
        engine_stub,
        handlers=_handlers,
        debug=options.debug
    )


if __name__ == '__main__':
    options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    ioloop.IOLoop.current().start()
