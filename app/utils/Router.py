# -*- coding: utf-8 -*-

from collections import namedtuple
from tornado.routing import Router, Matcher, RuleRouter, Rule, PathMatches


Resolve = namedtuple('Resolve', ['filename', 'linenum', 'paths'])


def dict_decode_values(_dict):
    """
    {'foo': b'bar'} => {'foo': 'bar'}
    """
    return {
        key: value.decode('utf-8')
        for key, value in _dict.items()
    }


class CustomRouter(Router):
    def __init__(self, filename, linenum):
        self.filename = filename
        self.linenum = linenum

    def find_handler(self, request, **kwargs):
        return Resolve(
            filename=self.filename,
            linenum=self.linenum,
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
                PathMatches(route.endpoint),
                CustomRouter(route.filename, route.linenum)
            ) for route in routes
        ]
        # create a new rule by method mapping to many rule by path
        method_rules.append(Rule(MethodMatches(method), RuleRouter(rules)))

    router = RuleRouter(method_rules)

    return router
