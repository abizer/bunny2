# Utility functions for transformations

from typing import List, Any
import re
import random
from .plugins import plugin_registry


class path_dispatcher:
    def _dispatch(self, processors: List[Any], path: str, payload: bytes):
        # first process all the regex-based rules
        for name, (pattern, fn) in processors.items():
            found = pattern.match(path)
            if found:
                logging.debug(f"dispatching {path} to {name}")
                try:
                    return fn(self, payload, *found.groups())
                except Exception as e:
                    logging.error(f"error processing {path} with {name}: {e}")
                    return e

        # default case: reflection
        return path

    def run(self, path: str, payload: bytes):
        return self._dispatch(plugin_registry, path, payload)


def transform_path_to_slug(path: str, payload: bytes = None) -> str:
    """converts the given path to a slug for database lookup

    to maintain consistency, the same function is used on both read and write paths.
    on the write path, the additional context from the payload may be used for deriving
      new slugs on known patterns.

    default behavior is that the request path is the slug
    transform_path_to_slug("exploring") -> "exploring"

    slugs can be aliased to other slugs
    transform_path_to_slug("h5") -> "/hobby/5"

    can implement a pattern-based shorturl generator
    transform_path_to_slug("shorten", "https://docs.google.com/...") -> "/g/ef45gh"

    do arbitrary work, like curl-able pastebin
    transform_path_to_slug("paste", <file contents>) -> "/p/abd4f5b32"
    transform_path_to_slug("pasted/debuglogs", <file contents>) -> "/p/20230823/debuglogs"

    it's expected that the single argument call produces only readable slugs and the
    double argument call produces only writable slugs
    """

    return path_dispatcher().run(path, payload)


def transform_payload_to_url(payload: bytes) -> str:
    """convert the given payload to a url

    eventually this will be extended so that, e.g. files can be
    piped into the shorten endpoint and this function will write it
    to a pastebin and then return the URL for redirection.

    right now, it just assumes the payload is a URL and returns it.
    """
    is_url = payload[:4] == b"http"

    if is_url:
        return bytes.decode(payload).strip()
