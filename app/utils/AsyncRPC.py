# -*- coding: utf-8 -*-

# https://github.com/grpc/grpc/issues/7910#issuecomment-243290904

import grpc
from grpc._cython import cygrpc
from grpc._channel import _handle_event, _EMPTY_FLAGS
from tornado.concurrent import Future
from tornado.ioloop import IOLoop

import types

def patch_iterator(it, ioloop=None):
    '''Changes gRPC stream iterator to return futures instead of blocking'''

    if ioloop is None:
        ioloop = IOLoop.current()

    # mostly identical to grpc._channel._event_handler
    def _tornado_event_handler(state, call, response_deserializer, fut):
        def handle_event(event):
            with state.condition:
                callbacks = _handle_event(event, state, response_deserializer)
                state.condition.notify_all()
                done = not state.due
                _process_future(state, fut) # this is the key patch point
            for callback in callbacks:
                callback()
            return call if done else None
        return handle_event

    # mostly identical to last part of grpc._channel._Rendevous._next
    def _process_future(state, fut):
        if state.response is not None:
            response = state.response
            state.response = None
            ioloop.add_callback(fut.set_result, response)
        elif cygrpc.OperationType.receive_message not in state.due:
            if state.code is grpc.StatusCode.OK:
                ioloop.add_callback(fut.set_exception, StopIteration())
            elif state.code is not None:
                ioloop.add_callback(fut.set_exception, self)

    # mostly identical to first part of grpc._channel._Rendevous._next
    def _next(self):
        # ensure there is only one outstanding request at any given time, or segfault happens
        if cygrpc.OperationType.receive_message in self._state.due:
            raise ValueError('Prior future was not resolved')

        # this method is the same as the first part of _Rendevous._next
        with self._state.condition:
            if self._state.code is None:
                fut = Future()
                event_handler = _tornado_event_handler(
                        self._state, self._call, self._response_deserializer, fut)
                self._call.start_client_batch(
                        cygrpc.Operations(
                                (cygrpc.operation_receive_message(_EMPTY_FLAGS),)),
                        event_handler)
                self._state.due.add(cygrpc.OperationType.receive_message)
                return fut
            elif self._state.code is grpc.StatusCode.OK:
                raise StopIteration()
            else:
                raise self

    # patch the iterator
    it._next = types.MethodType(_next, it)
