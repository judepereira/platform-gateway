# -*- coding: utf-8 -*-

from collections import namedtuple
from tornado.routing import Router, Matcher, RuleRouter, Rule, PathMatches


Route = namedtuple('Route', ['filename', 'start', 'paths'])


def dict_decode_values(_dict):
    """
    {'foo': b'bar'} => {'foo': 'bar'}
    """
    return {
        key: value.decode('utf-8')
        for key, value in _dict.items()
    }


class CustomRouter(Router):
    def __init__(self, filename, start_line):
        self.filename = filename
        self.start_line = start_line

    def find_handler(self, request, **kwargs):
        return Route(
            filename=self.filename,
            start=self.start_line,
            paths=dict_decode_values(kwargs.get('path_kwargs', {}))
        )


class MethodMatches(Matcher):
    """Matches requests method"""

    def __init__(self, method):
        self.method = method.upper()

    def match(self, request):
        if request.method == self.method:
            return {}
        else:
            return None


def make_router(routing_table):
    """Resolves a uri to the Story and line number to execute."""

    method_rules = []
    for method, routes in routing_table.items():
        rules = [
            Rule(
                PathMatches(route[0]),
                CustomRouter(route[1], route[2])
            ) for route in routes
        ]
        # create a new rule by method mapping to many rule by path
        method_rules.append(Rule(MethodMatches(method), RuleRouter(rules)))

    router = RuleRouter(method_rules)

    return router
