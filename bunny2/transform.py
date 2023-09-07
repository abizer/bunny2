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
                print(f"dispatching to {name}")
                return fn(self, payload, *found.groups())

        # default case: reflection
        return path

    def run(self, path: str, payload: bytes):
        return self._dispatch(plugin_registry, path, payload)

def transform_path_to_slug(path: str, payload: bytes = None) -> str:
    """
    Converts the given path to a slug that can be looked up in the database.
    To maintain consistency, the same function is used on both read and write paths.
    On the write path, the additional context from the payload may be used for deriving
      new slugs on known patterns.
    
    default behavior is that the request path is the slug
    transform_path_to_slug("exploring") -> "exploring"

    slugs can be aliased to other slugs 
    transform_path_to_slug("h5") -> "/hobby/5"

    can implement a pattern-based shorturl generator
    transform_path_to_slug("shorturl", "https://docs.google.com/...") -> "/g/ef45gh"

    do arbitrary work, like curl-able pastebin
    transform_path_to_slug("paste", <file contents>) -> "/p/abd4f5b32"
    transform_path_to_slug("pasted/debuglogs", <file contents>) -> "/p/20230823/debuglogs"

    it's expected that the single argument call produces only readable slugs and the
    double argument call produces only writable slugs
    """

    return path_dispatcher().run(path, payload)
    


def transform_payload_to_url(payload: bytes) -> str:
    """
    Converts the given payload to a URL.
    As per the current plan, it returns the payload as is.
    
    Args:
    payload (str): The payload to be transformed.
    
    Returns:
    str: The transformed URL.
    """
    is_url = payload[:4] == b"http"

    if is_url:
        return bytes.decode(payload).strip()
    
