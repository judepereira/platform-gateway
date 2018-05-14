# -*- coding: utf-8 -*-

import os
from tornado import ioloop
from tornado.options import define, options

from .App import App
from .utils.Stub import GrpcStub
from . import handlers


define('debug', default=False, help='enable debug')
define('port',
       default=int(os.getenv('PORT', '8888')),
       help='port to listen on')
define('engine',
       default=os.getenv('ENGINE', 'engine:50051'),
       help='engine hostname:port')
define('routes_file',
       default=os.getenv('ROUTES_FILE',
                         os.path.join(os.path.dirname(__file__),
                                      '../routes.cache')),
       help='file location for caching routes')


def make_app():
    engine_stub = GrpcStub(options.engine)

    _handlers = [
        (r'/\+', handlers.RegisterHandler),
        (r'/(?P<is_file>~/)?(?P<path>.*)', handlers.ExecHandler)
    ]

    return App(
        engine_stub,
        handlers=_handlers,
        debug=options.debug,
        routes_file=options.routes_file
    )


if __name__ == '__main__':
    options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    ioloop.IOLoop.current().start()
