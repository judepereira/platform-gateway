import os
import tornado.options
from tornado import ioloop
from json import dumps, loads, load
from tornado import web
from tornado.gen import coroutine, Future

from .Exec import ExecAsync
from .Uri import UriResolver, Resolve
from .Stub import GrpcStub


Resolver = None

Engine = None


class ExecHandler(web.RequestHandler):
    def resolve_path(self, path):
        """
        A http request to `/*` will resolve to one listener on that channel.
        """
        resolve = Resolver(self.request.method, path)
        if not resolve:
            # exit: path not being followed
            if self.request.method == 'GET':
                raise web.HTTPError(404)
            else:
                raise web.HTTPError(405)

        # [TODO] self.request.files -> /asyncy/tmp/:uuid/files/...
        files = {}

        context = {
            'request': {
                'method': self.request.method,
                'uri': self.request.uri,
                'paths': resolve.paths,
                'body': self.request.body.decode('utf-8'),
                'files': files,
                'arguments': {k: self.get_argument(k) for k in self.request.arguments},
                'headers': dict(self.request.headers)
            },
            'response': {
                # [TODO] map methods back
                'write(data:*)': None,
                'status(code:int)': None,
                'finish()': None
            }
        }

        return resolve, context

    def resolve_story(self, story):
        """
        A http request to `/~/folder/story:3` will directly execute that story.
        """
        if ':' in story:
            story, start = tuple(story.split(':', 1))
        else:
            start = 1
        resolve = Resolve(story, start, {})
        try:
            context = loads(self.request.body.decode('utf-8'))
        except:
            context = self.request.body.decode('utf-8')

        return resolve, context

    @coroutine
    def handle(self, path=None, story=None):
        if path:
            # resolve to http listeners
            resolve, context = self.resolve_path(path)
        else:
            # resolve directly to story
            resolve, context = self.resolve_story(story)

        # geneate the grpc parameters
        param = {
            'story_name': resolve.story_name,
            'start': resolve.start,
            'json_context': context
        }
        param = dumps(param)

        result = yield ExecAsync(
            Engine.RunStory.future(param, 30))

        self.finish(result)

    @coroutine
    def head(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def get(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def post(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def delete(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def patch(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def put(self, path=None, story=None):
        yield self.handle(path, story)

    @coroutine
    def options(self, path=None, story=None):
        yield self.handle(path, story)



def make_app():
    config_dir = os.getenv('CONFIG_DIR', '/asyncy/config')
    engine_endpoint = os.getenv('ENGINE', 'engine:50051')
    debug = os.getenv('DEBUG', False)

    routes = load(open(os.path.join(config_dir, 'routes.json')))

    global Resolver, Engine
    Resolver = UriResolver(**routes)
    Engine = GrpcStub(engine_endpoint)

    return web.Application(
        [
            (r'/~/(?P<story>.*)', ExecHandler),
            (r'/(?P<path>.*)', ExecHandler)
        ],
        debug=debug
    )


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(8888)
    ioloop.IOLoop.current().start()
