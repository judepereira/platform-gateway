from collections import namedtuple


Resolve = namedtuple('Resolve', ['story_name', 'start', 'paths'])


def UriResolver(**method_mapping):
    '''
    Resolves a uri to the Story and line number to execute.

    Usage::

        r = UriResolver(get={
            '/': ('index.story', 2),
            '/foo/*': ('other.story', 10)
        })
        r('/')
        >>> ('index.story', 2)
        r('/foo/bar')
        >>> ('other.story', 10)
        r('/foo')
        >>> None
    '''
    def _resolve(method, uri):
        mapping = method_mapping.get(method.lower())
        if mapping:

            # [TODO] find the correct location to map to
            res = ('server.story', 2)

            return Resolve(
                story_name=res[0],
                start=res[1],
                paths={
                    # [TODO] dict of named paths via (?P<key>regexp)
                }
            )
    return _resolve
