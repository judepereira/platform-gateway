# -*- coding: utf-8 -*-
from json import dumps
from raven.contrib.tornado import SentryMixin
from tornado.gen import coroutine, Return
from tornado.web import RequestHandler, HTTPError
from tornado.log import app_log

from ..utils.Router import Resolve
from ..utils.AsyncRPC import patch_iterator


class ExecHandler(SentryMixin, RequestHandler):
    def get_request_body(self):
        if 'multipart/form-data' in self.request.headers.get('Content-Type'):
            return self.request.files
        else:
            return self.request.body.decode('utf-8')

    def resolve_by_uri(self, path):
        """
        A http request to `/*` will resolve to one listener on that channel.
        """
        resolve = self.application.router.find_handler(self.request)

        app_log.info('Resolving to %s' % repr(resolve))

        if not resolve:
            # exit: path not being followed
            if self.request.method == 'GET':
                raise HTTPError(404)
            else:
                raise HTTPError(405)

        context = {
            'request': {
                'method': self.request.method,
                'uri': self.request.uri,
                'paths': resolve.paths,
                'body': self.get_request_body(),
                'arguments': {k: self.get_argument(k) for k in self.request.arguments},
                'headers': dict(self.request.headers)
            },
            'response': {
                'write()': {
                    'input': {
                        'data': {
                            'type': 'any'
                        }
                    }
                },
                'status()': {
                    'input': {
                        'code': {
                            'type': 'int'
                        }
                    }
                },
                'finish()': {}
            }

        }

        return resolve, context

    def resolve_by_filename(self, path):
        """
        A http request to `/~/folder/story:3` will directly execute that story.
        """
        if ':' in path:
            path, linenum = tuple(path.split(':', 1))
        else:
            linenum = 1

        # [TODO] HTTPError(404) if filename does not exist

        resolve = Resolve(
            filename=path,
            linenum=linenum,
            paths=None
        )

        context = self.get_request_body()

        return resolve, context

    @coroutine
    def _handle(self, is_file, path):
        if is_file:
            # resolve directly to story by pathname
            resolve, context = self.resolve_by_filename(path)
        else:
            # resolve to http listeners
            resolve, context = self.resolve_by_uri(path)

        # geneate the grpc parameters
        params = {
            'story_name': resolve.filename,
            'start': resolve.linenum,
            'json_context': context
        }
        params = dumps(params)

        stream = self.application.engine.RunStory(params)
        patch_iterator(stream)
        for result in stream
            try:
                self.rpc_callback((yield result))
            except (Return, StopIteration):
                break

        self.finish()

    def rpc_callback(self, result):
        if result.command == 'set_status':
            self.set_status(result.args.status)

        elif result.command == 'set_header':
            self.set_header(result.args.name, result.args.value)

        elif result.command == 'write':
            self.write(result.args.content)

        elif result.command == 'finish':
            raise Return()

    @coroutine
    def head(self, is_file, path):
        yield self._handle(is_file, path)

    @coroutine
    def get(self, is_file, path):
        yield self._handle(is_file, path)

    @coroutine
    def post(self, is_file, path):
        yield self._handle(is_file, path)

    @coroutine
    def delete(self, is_file, path):
        yield self._handle(is_file, path)

    @coroutine
    def patch(self, is_file, path):
        yield self._handle(is_file, path)

    @coroutine
    def put(self, is_file, path):
        yield self._handle(is_file, path)

    def options(self, is_file, path):
        """
        Returns the allowed options for this endpoint
        """
        self.set_header('Allow', 'GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS')
        # [FUTURE] http://zacstewart.com/2012/04/14/http-options-method.html
        self.finish()
